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


if __name__ == '__main__':
    unittest.main()
