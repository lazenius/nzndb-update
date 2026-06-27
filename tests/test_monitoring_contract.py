import unittest
from pathlib import Path


class MonitoringContractDocTest(unittest.TestCase):
    def setUp(self):
        self.text = Path('UPDATE_ROBOCODE_ADMIN_SPLIT.md').read_text()

    def test_includes_career_status_sql_contract(self):
        self.assertIn("## 7. robocode-admin 1차 데이터 계약 고정", self.text)
        self.assertIn("SELECT 'code_list' AS table_name, COUNT(*) AS row_count, MAX(recv_time) AS last_recv_time", self.text)
        self.assertIn("FROM CAREER_DB.subject_list;", self.text)

    def test_includes_academyinfo_status_sql_contract(self):
        self.assertIn("SELECT 'year_list' AS table_name, COUNT(*) AS row_count, MAX(year_val) AS latest_year, MAX(recv_time) AS last_recv_time", self.text)
        self.assertIn("FROM ACADEMYINFO_DB.startup_support_list;", self.text)
        self.assertIn("school_indicator_list", self.text)

    def test_includes_log_rules_and_429_policy(self):
        self.assertIn("/var/www/html/update/career/logs/", self.text)
        self.assertIn("/var/www/html/update/academyinfo/logs/", self.text)
        self.assertIn("기존 로그 문자열 규칙", self.text)
        self.assertIn("HTTP 429", self.text)
        self.assertIn("sync-school-indicators batch offset=", self.text)


if __name__ == '__main__':
    unittest.main()
