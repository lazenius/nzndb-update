import importlib.util
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import pymysql


BASE_DIR = Path(__file__).resolve().parents[1]
INCLUDE_DIR = Path(__file__).resolve().parent


def load_config():
    module_path = INCLUDE_DIR / 'common_local.py'
    if not module_path.exists():
        raise FileNotFoundError(
            f'설정 파일이 없습니다: {module_path} (common_local.py.example 복사 후 값 설정 필요)'
        )

    spec = importlib.util.spec_from_file_location('career_common_local', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONFIG = None
DB_HOST = ''
DB_USER = ''
DB_PASS = ''
DB_PORT = 3306
DB_NAME = 'CAREER_DB'
API_KEY = ''
BASE_API_URL = 'https://www.career.go.kr'
RAW_DIR = BASE_DIR / 'raw'
LOG_DIR = BASE_DIR / 'logs'


def ensure_config_loaded():
    global CONFIG, DB_HOST, DB_USER, DB_PASS, DB_PORT, DB_NAME, API_KEY, BASE_API_URL, RAW_DIR, LOG_DIR
    if CONFIG is not None:
        return

    CONFIG = load_config()
    DB_HOST = getattr(CONFIG, 'DB_HOST')
    DB_USER = getattr(CONFIG, 'DB_USER')
    DB_PASS = getattr(CONFIG, 'DB_PASS')
    DB_PORT = int(getattr(CONFIG, 'DB_PORT', 3306))
    DB_NAME = getattr(CONFIG, 'DB_NAME', 'CAREER_DB')
    API_KEY = getattr(CONFIG, 'API_KEY')
    BASE_API_URL = getattr(CONFIG, 'BASE_API_URL', 'https://www.career.go.kr').rstrip('/')
    RAW_DIR = Path(getattr(CONFIG, 'RAW_DIR', BASE_DIR / 'raw'))
    LOG_DIR = Path(getattr(CONFIG, 'LOG_DIR', BASE_DIR / 'logs'))


def now_text():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def log(message):
    print(f'[{now_text()}] {message}', flush=True)


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def connect_db(database=None, autocommit=False):
    ensure_config_loaded()
    kwargs = {
        'host': DB_HOST,
        'user': DB_USER,
        'password': DB_PASS,
        'port': DB_PORT,
        'charset': 'utf8mb4',
        'autocommit': autocommit,
        'cursorclass': pymysql.cursors.DictCursor,
    }
    if database:
        kwargs['database'] = database
    return pymysql.connect(**kwargs)


def text(value):
    if value is None:
        return ''
    value = str(value).strip()
    if value.lower() == 'null':
        return ''
    return value


def int_or_zero(value):
    value = text(value).replace(',', '')
    if value == '':
        return 0
    try:
        return int(float(value))
    except ValueError:
        return 0


def float_or_zero(value):
    value = text(value).replace(',', '')
    if value == '':
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def first_non_empty(*values):
    for value in values:
        value = text(value)
        if value != '':
            return value
    return ''


def ensure_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def ensure_dict(value):
    if isinstance(value, dict):
        return value
    return {}


def build_front_url(path, params=None):
    ensure_config_loaded()
    params = dict(params or {})
    params['apiKey'] = API_KEY
    query = urlencode(params)
    return f'{BASE_API_URL}/cnet/front/openapi/{path}.json?{query}'


def build_legacy_url(params=None):
    ensure_config_loaded()
    merged = {
        'apiKey': API_KEY,
        'svcType': 'api',
        'contentType': 'json',
    }
    if params:
        merged.update(params)
    query = urlencode(merged)
    return f'{BASE_API_URL}/cnet/openapi/getOpenApi?{query}'


def fetch_json_url(url):
    with urlopen(url, timeout=120) as response:
        return response.read()


def fetch_front_json(path, params=None):
    url = build_front_url(path, params)
    return url, json.loads(fetch_json_url(url).decode('utf-8'))


def fetch_legacy_json(params=None):
    url = build_legacy_url(params)
    return url, json.loads(fetch_json_url(url).decode('utf-8'))


def save_raw(job_name, file_name, payload):
    ensure_config_loaded()
    ensure_dir(RAW_DIR / job_name)
    target = RAW_DIR / job_name / file_name
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    latest = RAW_DIR / job_name / 'latest.json'
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return target


def safe_url(url):
    for key_name in ('apiKey=', 'apikey='):
        if key_name not in url:
            continue
        head, tail = url.split(key_name, 1)
        if '&' in tail:
            _, rest = tail.split('&', 1)
            return f'{head}{key_name}***&{rest}'
        return f'{head}{key_name}***'
    return url
