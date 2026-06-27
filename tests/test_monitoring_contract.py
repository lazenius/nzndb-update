import unittest
from pathlib import Path


class MonitoringContractDocTest(unittest.TestCase):
    def setUp(self):
        self.split_text = Path('UPDATE_ROBOCODE_ADMIN_SPLIT.md').read_text()
        self.contract_text = Path('UPDATE_MONITORING_DATA_CONTRACT.md').read_text()

    def test_includes_career_status_sql_contract(self):
        self.assertIn("## 7. robocode-admin 1차 데이터 계약 고정", self.split_text)
        self.assertIn("SELECT 'code_list' AS table_name, COUNT(*) AS row_count, MAX(recv_time) AS last_recv_time", self.split_text)
        self.assertIn("FROM CAREER_DB.subject_list;", self.split_text)

    def test_includes_academyinfo_status_sql_contract(self):
        self.assertIn("SELECT 'year_list' AS table_name, COUNT(*) AS row_count, MAX(year_val) AS latest_year, MAX(recv_time) AS last_recv_time", self.split_text)
        self.assertIn("FROM ACADEMYINFO_DB.startup_support_list;", self.split_text)
        self.assertIn("MAX(indct_yr)", self.split_text)
        self.assertIn("school_indicator_list", self.split_text)

    def test_includes_log_rules_and_429_policy(self):
        self.assertIn("/var/www/html/update/career/logs/", self.split_text)
        self.assertIn("/var/www/html/update/academyinfo/logs/", self.split_text)
        self.assertIn("기존 로그 문자열 규칙", self.split_text)
        self.assertIn("HTTP 429", self.split_text)
        self.assertIn("sync-school-indicators batch offset=", self.split_text)

    def test_includes_library_to_page_mapping_and_smoke_rules(self):
        self.assertIn("조회 라이브러리 ↔ 페이지 연결 기준", self.split_text)
        self.assertIn("nznlab/db/career/status.inc", self.split_text)
        self.assertIn("robocode-admin/db/career_status.php", self.split_text)
        self.assertIn("collector_runs.php", self.split_text)

    def test_contract_doc_tracks_indicator_year_and_log_contract(self):
        self.assertIn("SELECT MAX(indct_yr) AS latest_indicator_year", self.contract_text)
        self.assertIn("sync_school_indicator_batch.log", self.contract_text)
        self.assertIn("HTTP 429", self.contract_text)


if __name__ == '__main__':
    unittest.main()
