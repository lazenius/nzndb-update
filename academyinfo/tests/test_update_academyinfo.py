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


if __name__ == '__main__':
    unittest.main()
