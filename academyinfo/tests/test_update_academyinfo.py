import importlib.util
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = BASE_DIR / 'update_academyinfo.py'


def load_module():
    sys.path.insert(0, str(BASE_DIR))
    spec = importlib.util.spec_from_file_location('academyinfo_update_academyinfo', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UpdateAcademyinfoTest(unittest.TestCase):
    def test_startup_support_schema_has_school_year_index(self):
        module = load_module()

        self.assertTrue(any(
            'CREATE TABLE IF NOT EXISTS' in statement
            and 'startup_support_list' in statement
            and 'KEY schl_year_idx (schl_id, svy_yr)' in statement
            for statement in module.CREATE_STATEMENTS
        ))

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

    def test_sync_school_master_commits_per_unit(self):
        module = load_module()
        commits = []
        visited = []

        module.resolve_school_master_years = lambda cur, endpoint, scope: (['2025'], {'2025': [
            {'schlId': '0001', 'svyYr': '2025', 'schlKrnNm': '학교1', 'schlFullNm': '학교1'},
        ]})
        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
        ]

        def fake_fetch(endpoint, params, job_name):
            visited.append((endpoint['path'], params.get('schlId', params.get('svyYr'))))
            return [{
                'schlId': params.get('schlId', '0001'),
                'svyYr': params.get('svyYr', '2025'),
                'schlNm': '학교',
            }]

        module.fetch_pages = fake_fetch
        module.upsert_school_row = lambda cur, row: None
        module.commit_cursor = lambda cur: commits.append('commit')
        module.log = lambda message: None

        endpoints = [
            {'path': '/getUniversityCode', 'required_params': []},
            {'path': '/getSchoolInfo', 'required_params': ['schlKrnNm']},
        ]

        module.sync_school_master(None, endpoints, 'latest')

        self.assertEqual([
            ('/getSchoolInfo', '0001'),
            ('/getSchoolInfo', '0002'),
        ], visited)
        self.assertEqual(['commit', 'commit', 'commit'], commits)

    def test_sync_school_indicators_records_429_and_continues(self):
        module = load_module()
        visited = []
        commits = []
        logs = []

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
        module.record_school_indicator_skip = lambda *args: None
        module.log = lambda message: logs.append(message)
        module.commit_cursor = lambda cur: commits.append('commit')

        module.sync_school_indicators(
            None,
            [{'path': '/getComparisonLibraryBudgetCrntSt', 'required_params': []}],
            'latest',
        )

        self.assertEqual(['0001', '0002'], visited)
        self.assertEqual(['commit', 'commit', 'commit'], commits)
        self.assertIn('sync-school-indicators batch offset=0 limit=all count=2', logs)
        self.assertIn('/getComparisonLibraryBudgetCrntSt 0002/2025 HTTP 429 - offset=0 limit=all count=2 요청 스킵 후 계속', logs)
        self.assertIn('sync-school-indicators batch completed offset=0 limit=all count=2 processed_schools=2 skipped_requests=1', logs)

    def test_sync_school_indicators_throttles_each_request(self):
        module = load_module()
        sleeps = []

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
        ]
        module.load_indicator_codes = lambda cur: []
        module.fetch_pages = lambda endpoint, params, job_name: []
        module.upsert_school_indicator = lambda cur, api_id, item, params: None
        module.commit_cursor = lambda cur: None
        module.log = lambda message: None
        module.time.sleep = lambda seconds: sleeps.append(seconds)

        module.sync_school_indicators(
            None,
            [{'path': '/getComparisonFullTimeFacultyResearchCrntSt', 'required_params': []}],
            'latest',
        )

        self.assertEqual([module.school_indicator_request_delay('/getComparisonFullTimeFacultyResearchCrntSt')], sleeps)

    def test_sync_school_indicators_uses_school_batch(self):
        module = load_module()
        visited = []
        logs = []

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
            {'schl_id': '0003', 'svy_yr': '2025', 'name': '학교3'},
        ]
        module.load_indicator_codes = lambda cur: []
        module.fetch_pages = lambda endpoint, params, job_name: visited.append((endpoint['path'], params['schlId'])) or []
        module.upsert_school_indicator = lambda cur, api_id, item, params: None
        module.log = lambda message: logs.append(message)
        module.commit_cursor = lambda cur: None

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
        self.assertIn('sync-school-indicators batch completed offset=1 limit=1 count=1 processed_schools=1 skipped_requests=0', logs)

    def test_sync_startup_support_uses_school_batch(self):
        module = load_module()
        visited = []

        module.load_schools = lambda cur, scope='latest': [
            {'schl_id': '0001', 'svy_yr': '2025', 'name': '학교1'},
            {'schl_id': '0002', 'svy_yr': '2025', 'name': '학교2'},
            {'schl_id': '0003', 'svy_yr': '2025', 'name': '학교3'},
        ]
        module.fetch_pages = lambda endpoint, params, job_name: visited.append((endpoint['path'], params['schlId'])) or []
        module.insert_startup_support = lambda cur, rows: None
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

    def test_insert_startup_support_batches_rows(self):
        module = load_module()
        batches = []

        class Cursor:
            def executemany(self, query, rows):
                batches.append(rows)

        rows = [('api', 'school', '2025', 'indicator', '2025', index, 'key', 'value') for index in range(2501)]
        module.insert_startup_support(Cursor(), rows, batch_size=1000)

        self.assertEqual([1000, 1000, 501], [len(batch) for batch in batches])

    def test_build_startup_support_rows_flattens_item(self):
        module = load_module()

        rows = module.build_startup_support_rows(
            'api',
            {'schlId': '0001', 'svyYr': '2025', 'indctId': 'indicator', 'field': 'value'},
            {},
            3,
        )

        self.assertEqual(4, len(rows))
        self.assertEqual(('api', '0001', '2025', 'indicator'), rows[0][:4])
        self.assertEqual(3, rows[0][5])


if __name__ == '__main__':
    unittest.main()
