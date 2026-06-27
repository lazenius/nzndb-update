import importlib.util
import unittest
from pathlib import Path
from urllib.error import HTTPError

BASE_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = BASE_DIR / 'include' / 'common.py'


def load_module():
    spec = importlib.util.spec_from_file_location('academyinfo_common', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommonFetchXmlTest(unittest.TestCase):
    def test_fetch_xml_retries_http_429_then_succeeds(self):
        module = load_module()
        sleeps = []
        logs = []
        attempts = []

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'<xml />'

        def fake_urlopen(url, timeout=120):
            attempts.append((url, timeout))
            if len(attempts) < 3:
                raise HTTPError(url, 429, 'Too Many Requests', None, None)
            return FakeResponse()

        module.ensure_config_loaded = lambda: None
        module.build_url = lambda service_host, endpoint_path, params: 'https://example.test/api'
        module.urlopen = fake_urlopen
        module.time.sleep = lambda seconds: sleeps.append(seconds)
        module.log = lambda message: logs.append(message)

        url, payload = module.fetch_xml('service', '/endpoint', {'serviceKey': 'k'})

        self.assertEqual('https://example.test/api', url)
        self.assertEqual(b'<xml />', payload)
        self.assertEqual([2, 5], sleeps)
        self.assertEqual(3, len(attempts))
        self.assertEqual([
            '재시도 예정: HTTP 429 /endpoint attempt=1',
            '재시도 예정: HTTP 429 /endpoint attempt=2',
        ], logs)


if __name__ == '__main__':
    unittest.main()
