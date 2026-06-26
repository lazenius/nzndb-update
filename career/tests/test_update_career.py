import importlib.util
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = BASE_DIR / 'update_career.py'


def load_module():
    sys.path.insert(0, str(BASE_DIR))
    spec = importlib.util.spec_from_file_location('career_update_career', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UpdateCareerTest(unittest.TestCase):
    def test_safe_url_masks_apikey_lowercase(self):
        module = load_module()

        safe = module.common.safe_url('https://example.com/test?apikey=secret&q=33')

        self.assertEqual('https://example.com/test?apikey=***&q=33', safe)

    def test_build_parser_accepts_sync_aptitude_meta(self):
        module = load_module()

        args = module.build_parser().parse_args([
            'sync-aptitude-meta',
        ])

        self.assertEqual('sync-aptitude-meta', args.command)

    def test_build_parser_accepts_subject_detail_command(self):
        module = load_module()

        args = module.build_parser().parse_args([
            'sync-subject-detail',
            '--school', 'univ',
            '--seq', '8',
            '--limit', '3',
        ])

        self.assertEqual('sync-subject-detail', args.command)
        self.assertEqual('univ', args.school)
        self.assertEqual(8, args.seq)
        self.assertEqual(3, args.limit)

    def test_sync_subject_detail_requires_school_when_seq_given(self):
        module = load_module()

        with self.assertRaises(ValueError):
            module.sync_subject_detail(seq=8)

    def test_sync_aptitude_meta_uses_v2_test_list(self):
        module = load_module()
        calls = []
        commits = []

        class DummyCursor:
            connection = None

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        class DummyConn:
            def cursor(self):
                return DummyCursor()

            def commit(self):
                commits.append('commit')

            def close(self):
                commits.append('close')

        module.ensure_tables = lambda: None
        module.connect_db = lambda database=None: DummyConn()
        module.save_raw = lambda job_name, file_name, payload: None
        module.log = lambda message: None
        module.upsert_aptitude_test = lambda cur, version, row, question_count: calls.append(('test', version, row['qno'], question_count)) or row['qno']
        module.replace_aptitude_questions = lambda cur, version, qno, questions: calls.append(('question', version, qno, len(questions)))
        module.fetch_aptitude_v2_tests = lambda: ('https://example.com/tests', {
            'result': [
                {'qno': '33', 'name': '직업흥미검사(H)', 'target': '중학생'},
                {'qno': '34', 'name': '직업흥미검사(H)', 'target': '고등학생'},
            ]
        })

        def fake_detail(qno):
            return (f'https://example.com/test?q={qno}', {
                'result': {
                    'qnm': f'검사{qno}',
                    'summary': '설명',
                    'questions': [
                        {
                            'no': 1,
                            'title': '안내',
                            'text': '문항',
                            'limit': 1,
                            'choices': [
                                {'val': '1', 'text': '예', 'type': 'M'},
                            ],
                        }
                    ],
                }
            })

        module.fetch_aptitude_v2_test = fake_detail

        module.sync_aptitude_meta()

        self.assertEqual([
            ('test', 'v2', 33, 1),
            ('question', 'v2', 33, 1),
            ('test', 'v2', 34, 1),
            ('question', 'v2', 34, 1),
        ], calls)
        self.assertEqual(['commit', 'close'], commits)


if __name__ == '__main__':
    unittest.main()
