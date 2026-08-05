import argparse
import importlib.util
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError

BASE_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = BASE_DIR / 'update_academyinfo.py'


def load_module():
    sys.path.insert(0, str(BASE_DIR))
    spec = importlib.util.spec_from_file_location('academyinfo_update_academyinfo', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stub_attempt_ledger(module, attempts=None):
    """school_indicator_attempt 대장 접근을 끊는다 (테스트는 cur=None으로 호출한다)."""
    recorded = []
    module.load_endpoint_last_attempt = lambda cur, api_id: dict(attempts or {})
    module.record_endpoint_attempt = lambda cur, api_id, school_id, svy_yr: recorded.append(
        (api_id, str(school_id), str(svy_yr))
    )
    return recorded


class UpdateAcademyinfoTest(unittest.TestCase):
    def test_classify_series_system_as_metadata(self):
        module = load_module()

        endpoint = {
            'path': '/getCodeBySeriesSystem',
            'host': 'https://www.career.go.kr',
            'required_params': ['svyYr'],
            'optional_params': [],
        }

        self.assertEqual('metadata', module.classify(endpoint))

    def test_build_parser_accepts_school_batch_options(self):
        module = load_module()

        args = module.build_parser().parse_args([
            'sync-subject-master',
            '--scope', 'latest',
            '--school-offset', '10',
            '--school-limit', '5',
        ])

        self.assertEqual(10, args.school_offset)
        self.assertEqual(5, args.school_limit)

    def test_sync_subject_master_uses_school_batch(self):
        module = load_module()
        visited = []

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
            {'schl_id': '0003', 'svy_yr': '2025', 'name': '학교3'},
        ]
        module.fetch_pages = lambda endpoint, params, job_name: visited.append((endpoint['path'], params['schlId'])) or []
        module.subject_seed_from_major_code = lambda cur, item: None
        module.subject_merge_from_school_major_info = lambda cur, schl_id, item: None
        module.log = lambda message: None

        endpoints = [
            {'path': '/getUniversityMajorCode', 'required_params': []},
            {'path': '/getSchoolMajorInfo', 'required_params': ['schlKrnNm']},
        ]

        module.sync_subject_master(None, endpoints, 'latest', school_offset=1, school_limit=1)

        self.assertEqual([
            ('/getUniversityMajorCode', '0002'),
            ('/getSchoolMajorInfo', '0002'),
        ], visited)


    def test_sync_school_indicators_commits_and_continues_on_429(self):
        module = load_module()
        visited = []
        commits = []

        class Http429(module.HTTPError):
            def __init__(self):
                super().__init__('http://example.com', 429, 'Too Many Requests', None, None)

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
        ]
        module.load_indicator_codes = lambda cur: []

        def fake_fetch(endpoint, params, job_name):
            visited.append(params['schlId'])
            if params['schlId'] == '0002':
                raise Http429()
            return []

        module.fetch_pages = fake_fetch
        module.upsert_school_indicator = lambda cur, api_id, item, params: None
        module.log = lambda message: None
        module.commit_cursor = lambda cur: commits.append('commit')
        stub_attempt_ledger(module)

        module.sync_school_indicators(
            None,
            [{'path': '/getComparisonLibraryBudgetCrntSt', 'required_params': []}],
            'latest',
        )

        self.assertEqual(['0001', '0002'], visited)
        # 0001 성공 후 1회, 0002의 429 skip 직후 1회, 0002 학교 종료 시 1회
        self.assertEqual(['commit', 'commit', 'commit'], commits)

    def test_sync_school_indicators_uses_school_batch(self):
        module = load_module()
        visited = []

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
            {'schl_id': '0003', 'svy_yr': '2025', 'name': '학교3'},
        ]
        module.load_indicator_codes = lambda cur: []
        module.fetch_pages = lambda endpoint, params, job_name: visited.append((endpoint['path'], params['schlId'])) or []
        module.upsert_school_indicator = lambda cur, api_id, item, params: None
        module.log = lambda message: None
        module.commit_cursor = lambda cur: None
        stub_attempt_ledger(module)

        module.sync_school_indicators(
            None,
            [{'path': '/getComparisonLibraryBudgetCrntSt', 'required_params': []}],
            'latest',
            school_offset=1,
            school_limit=1,
        )

        self.assertEqual([
            ('/getComparisonLibraryBudgetCrntSt', '0002'),
        ], visited)

    def test_sync_startup_support_uses_school_batch(self):
        module = load_module()
        visited = []

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
            {'schl_id': '0003', 'svy_yr': '2025', 'name': '학교3'},
        ]
        module.fetch_pages = lambda endpoint, params, job_name: visited.append((endpoint['path'], params['schlId'])) or []
        module.insert_startup_support = lambda cur, api_id, item, params, seq_no: None
        module.log = lambda message: None

        module.sync_startup_support(
            None,
            [{'path': '/getStupEdcSuptCstt', 'required_params': []}],
            'latest',
            school_offset=1,
            school_limit=1,
        )

        self.assertEqual([
            ('/getStupEdcSuptCstt', '0002'),
        ], visited)


class SelectStaleSchoolsTest(unittest.TestCase):
    def _schools(self):
        return [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
            {'schl_id': '0003', 'svy_yr': '2025', 'name': '학교3'},
        ]

    def test_never_collected_school_comes_first(self):
        module = load_module()

        # 0002만 미수집 → recv_time이 있는 나머지보다 먼저 선정돼야 한다
        last_recv = {
            '0001': datetime(2026, 8, 1),
            '0003': datetime(2026, 7, 1),
        }

        selected = module.select_stale_schools(self._schools(), last_recv, 1)

        self.assertEqual(['0002'], [s['schl_id'] for s in selected])

    def test_orders_by_oldest_recv_time(self):
        module = load_module()

        last_recv = {
            '0001': datetime(2026, 8, 1),
            '0002': datetime(2026, 6, 1),
            '0003': datetime(2026, 7, 1),
        }

        selected = module.select_stale_schools(self._schools(), last_recv, 3)

        self.assertEqual(['0002', '0003', '0001'], [s['schl_id'] for s in selected])

    def test_respects_limit(self):
        module = load_module()

        last_recv = {
            '0001': datetime(2026, 8, 1),
            '0002': datetime(2026, 6, 1),
            '0003': datetime(2026, 7, 1),
        }

        selected = module.select_stale_schools(self._schools(), last_recv, 2)

        self.assertEqual(['0002', '0003'], [s['schl_id'] for s in selected])

    def test_rejects_non_positive_limit(self):
        module = load_module()

        with self.assertRaises(ValueError):
            module.select_stale_schools(self._schools(), {}, 0)


class SyncSchoolIndicatorsStaleTest(unittest.TestCase):
    def silence_sleep(self, module):
        """time 모듈을 직접 대입하면 전역이 오염되므로 patch로 원복을 보장한다."""
        patcher = mock.patch.object(module.time, 'sleep')
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_stale_limit_selects_oldest_school(self):
        module = load_module()
        visited = []

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
            {'schl_id': '0003', 'svy_yr': '2025', 'name': '학교3'},
        ]
        module.load_school_last_recv = lambda cur: {
            '0001': datetime(2026, 8, 1),
            '0002': datetime(2026, 6, 1),
            '0003': datetime(2026, 7, 1),
        }
        module.load_indicator_codes = lambda cur: []
        module.fetch_pages = lambda endpoint, params, job_name: visited.append((endpoint['path'], params['schlId'])) or []
        module.upsert_school_indicator = lambda cur, api_id, item, params: None
        module.log = lambda message: None
        module.commit_cursor = lambda cur: None
        stub_attempt_ledger(module)
        self.silence_sleep(module)

        module.sync_school_indicators(
            None,
            [{'path': '/getComparisonLibraryBudgetCrntSt', 'required_params': []}],
            'latest',
            stale_limit=1,
        )

        self.assertEqual([
            ('/getComparisonLibraryBudgetCrntSt', '0002'),
        ], visited)

    def test_aborts_after_consecutive_skips(self):
        module = load_module()
        calls = []

        def raise_429(endpoint, params, job_name):
            calls.append(params.get('indctId'))
            raise HTTPError('http://example.com', 429, 'Too Many Requests', None, None)

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
        ]
        module.load_indicator_codes = lambda cur: ['a', 'b', 'c', 'd', 'e']
        module.fetch_pages = raise_429
        module.record_school_indicator_skip = lambda *a, **kw: None
        module.upsert_school_indicator = lambda cur, api_id, item, params: None
        module.log = lambda message: None
        module.commit_cursor = lambda cur: None
        # 이 테스트의 관심사는 연속 skip 중단이므로 indctId 화이트리스트는 비운다
        module.SCHOOL_INDICATOR_ENDPOINT_CODES = {}
        stub_attempt_ledger(module)
        self.silence_sleep(module)

        module.sync_school_indicators(
            None,
            [{'path': '/getComparisonFullTimeFacultyResearchCrntSt', 'required_params': ['indctId']}],
            'latest',
            school_limit=2,
            max_consecutive_skips=3,
        )

        # 연속 3건에서 중단 → 남은 지표코드·학교로 진행하지 않는다
        self.assertEqual(['a', 'b', 'c'], calls)

    def test_consecutive_skip_counter_resets_on_success(self):
        module = load_module()
        calls = []

        def sometimes_429(endpoint, params, job_name):
            calls.append(params.get('indctId'))
            # 'b' 만 성공 → 카운터가 리셋되어 중단되지 않아야 한다
            if params.get('indctId') == 'b':
                return []
            raise HTTPError('http://example.com', 429, 'Too Many Requests', None, None)

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
        ]
        module.load_indicator_codes = lambda cur: ['a', 'b', 'c']
        module.fetch_pages = sometimes_429
        module.record_school_indicator_skip = lambda *a, **kw: None
        module.upsert_school_indicator = lambda cur, api_id, item, params: None
        module.log = lambda message: None
        module.commit_cursor = lambda cur: None
        module.SCHOOL_INDICATOR_ENDPOINT_CODES = {}
        stub_attempt_ledger(module)
        self.silence_sleep(module)

        module.sync_school_indicators(
            None,
            [{'path': '/getComparisonFullTimeFacultyResearchCrntSt', 'required_params': ['indctId']}],
            'latest',
            max_consecutive_skips=2,
        )

        self.assertEqual(['a', 'b', 'c'], calls)


class EndpointBudgetTest(unittest.TestCase):
    """2026-08-05 도입: indctId 화이트리스트 · 엔드포인트 예산 · 429 브레이커 · 시도 대장."""

    def silence_sleep(self, module):
        patcher = mock.patch.object(module.time, 'sleep')
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_endpoint_indicator_codes_filters_to_whitelist(self):
        module = load_module()
        codes = ['1', '54', '66', '67', '99']

        self.assertEqual(
            ['66', '67'],
            module.endpoint_indicator_codes('/getComparisonFullTimeFacultyEnsureCrntSt', codes),
        )
        # 미등록 엔드포인트는 전체 코드를 그대로 쓴다
        self.assertEqual(codes, module.endpoint_indicator_codes('/getComparisonLibraryBudgetCrntSt', codes))

    def test_budget_limits_schools_by_fan_out(self):
        """예산 / 학교당 호출수 만큼만 처리하고, 시도가 오래된 학교를 먼저 고른다."""
        module = load_module()
        visited = []

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
            {'schl_id': '0003', 'svy_yr': '2025', 'name': '학교3'},
        ]
        module.load_indicator_codes = lambda cur: ['66', '67']
        module.fetch_pages = lambda endpoint, params, job_name: visited.append(params['schlId']) or []
        module.upsert_school_indicator = lambda cur, api_id, item, params: None
        module.log = lambda message: None
        module.commit_cursor = lambda cur: None
        # 0003 이 가장 오래됨, 0001 은 미시도(최우선)
        stub_attempt_ledger(module, attempts={
            '0002': datetime(2026, 8, 1),
            '0003': datetime(2026, 6, 1),
        })
        module.SCHOOL_INDICATOR_ENDPOINT_CALL_BUDGET = 4  # 학교당 2콜 → 2개교만
        self.silence_sleep(module)

        module.sync_school_indicators(
            None,
            [{'path': '/getComparisonFullTimeFacultyEnsureCrntSt', 'required_params': ['indctId']}],
            'latest',
        )

        # 미시도 0001 먼저, 그다음 오래된 0003. 0002 는 예산 밖
        self.assertEqual(['0001', '0001', '0003', '0003'], visited)

    def test_breaker_stops_only_the_saturated_endpoint(self):
        """연속 429 5건이면 그 엔드포인트만 포기하고 다음 엔드포인트는 계속한다."""
        module = load_module()
        visited = []

        def fetch(endpoint, params, job_name):
            visited.append((endpoint['path'], params['schlId']))
            if endpoint['path'] == '/saturated':
                raise HTTPError('http://example.com', 429, 'Too Many Requests', None, None)
            return []

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': f'{i:04d}', 'svy_yr': '2025', 'name': f'학교{i}'} for i in range(1, 9)
        ]
        module.load_indicator_codes = lambda cur: []
        module.fetch_pages = fetch
        module.record_school_indicator_skip = lambda *a, **kw: None
        module.upsert_school_indicator = lambda cur, api_id, item, params: None
        module.log = lambda message: None
        module.commit_cursor = lambda cur: None
        stub_attempt_ledger(module)
        self.silence_sleep(module)

        module.sync_school_indicators(
            None,
            [
                {'path': '/saturated', 'required_params': []},
                {'path': '/healthy', 'required_params': []},
            ],
            'latest',
        )

        saturated = [s for p, s in visited if p == '/saturated']
        healthy = [s for p, s in visited if p == '/healthy']
        self.assertEqual(module.SCHOOL_INDICATOR_ENDPOINT_429_BREAKER, len(saturated))
        self.assertEqual(8, len(healthy))

    def test_attempt_recorded_on_zero_rows_but_not_on_all_429(self):
        """0건 응답도 시도로 기록해야 회전이 돈다. 전부 429면 기록하지 않는다."""
        module = load_module()

        def fetch(endpoint, params, job_name):
            if params['schlId'] == '0002':
                raise HTTPError('http://example.com', 429, 'Too Many Requests', None, None)
            return []

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
        ]
        module.load_indicator_codes = lambda cur: []
        module.fetch_pages = fetch
        module.record_school_indicator_skip = lambda *a, **kw: None
        module.upsert_school_indicator = lambda cur, api_id, item, params: None
        module.log = lambda message: None
        module.commit_cursor = lambda cur: None
        recorded = stub_attempt_ledger(module)
        self.silence_sleep(module)

        module.sync_school_indicators(
            None,
            [{'path': '/getComparisonLibraryBudgetCrntSt', 'required_params': []}],
            'latest',
        )

        self.assertEqual([('getComparisonLibraryBudgetCrntSt', '0001', '2025')], recorded)


class ValidateArgsTest(unittest.TestCase):
    def _args(self, **overrides):
        base = {
            'job': 'sync-school-indicators',
            'stale_limit': 13,
            'school_offset': 0,
            'school_limit': None,
        }
        base.update(overrides)
        return argparse.Namespace(**base)

    def test_accepts_stale_limit_alone(self):
        module = load_module()

        module.validate_args(self._args())

    def test_rejects_stale_limit_with_school_offset(self):
        module = load_module()

        with self.assertRaises(ValueError):
            module.validate_args(self._args(school_offset=9))

    def test_rejects_stale_limit_with_school_limit(self):
        module = load_module()

        with self.assertRaises(ValueError):
            module.validate_args(self._args(school_limit=9))

    def test_rejects_stale_limit_on_other_job(self):
        module = load_module()

        with self.assertRaises(ValueError):
            module.validate_args(self._args(job='sync-startup-support'))

    def test_rejects_non_positive_stale_limit(self):
        module = load_module()

        with self.assertRaises(ValueError):
            module.validate_args(self._args(stale_limit=0))

    def test_ignores_when_stale_limit_absent(self):
        module = load_module()

        module.validate_args(self._args(stale_limit=None, school_offset=9, school_limit=9))


if __name__ == '__main__':
    unittest.main()
