import importlib.util
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODULE_PATH = BASE_DIR / 'update_career.py'


def load_module():
    sys.path.insert(0, str(BASE_DIR))
    spec = importlib.util.spec_from_file_location('career_update_career', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UpdateCareerTest(unittest.TestCase):
    def test_build_parser_accepts_school_and_subject_commands(self):
        module = load_module()

        school_args = module.build_parser().parse_args(['sync-school-list'])
        subject_args = module.build_parser().parse_args(['sync-subject-list'])

        self.assertEqual('sync-school-list', school_args.command)
        self.assertEqual('sync-subject-list', subject_args.command)

    def test_main_dispatches_school_and_subject_commands(self):
        module = load_module()
        visited = []

        module.build_parser = lambda: type('Parser', (), {
            'parse_args': lambda self: type('Args', (), {'command': 'sync-school-list'})(),
            'error': lambda self, message: (_ for _ in ()).throw(AssertionError(message)),
        })()
        module.sync_school_list = lambda: visited.append('school')
        module.sync_subject_list = lambda: visited.append('subject')

        module.main()

        module.build_parser = lambda: type('Parser', (), {
            'parse_args': lambda self: type('Args', (), {'command': 'sync-subject-list'})(),
            'error': lambda self, message: (_ for _ in ()).throw(AssertionError(message)),
        })()
        module.main()

        self.assertEqual(['school', 'subject'], visited)


if __name__ == '__main__':
    unittest.main()
