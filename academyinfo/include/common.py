import importlib.util
import os
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from xml.etree import ElementTree

import pymysql


BASE_DIR = Path(__file__).resolve().parents[1]
INCLUDE_DIR = Path(__file__).resolve().parent


def load_config():
    module_path = INCLUDE_DIR / 'common_local.py'
    if not module_path.exists():
        raise FileNotFoundError(
            f'설정 파일이 없습니다: {module_path} (common_local.py.example 복사 후 값 설정 필요)'
        )

    spec = importlib.util.spec_from_file_location('academyinfo_common_local', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONFIG = None
DB_HOST = ''
DB_USER = ''
DB_PASS = ''
DB_PORT = 3306
DB_NAME = 'ACADEMYINFO_DB'
SERVICE_KEY = ''
BASE_API_URL = 'https://apis.data.go.kr'
SERVICE_URL = ''
USE_SERVICE_URL = False
RAW_DIR = BASE_DIR / 'raw'
LOG_DIR = BASE_DIR / 'logs'


def ensure_config_loaded():
    global CONFIG, DB_HOST, DB_USER, DB_PASS, DB_PORT, DB_NAME, SERVICE_KEY, BASE_API_URL, SERVICE_URL, USE_SERVICE_URL, RAW_DIR, LOG_DIR
    if CONFIG is not None:
        return

    CONFIG = load_config()
    DB_HOST = getattr(CONFIG, 'DB_HOST')
    DB_USER = getattr(CONFIG, 'DB_USER')
    DB_PASS = getattr(CONFIG, 'DB_PASS')
    DB_PORT = int(getattr(CONFIG, 'DB_PORT', 3306))
    DB_NAME = getattr(CONFIG, 'DB_NAME', 'ACADEMYINFO_DB')
    SERVICE_KEY = getattr(CONFIG, 'SERVICE_KEY')
    BASE_API_URL = getattr(CONFIG, 'BASE_API_URL', 'https://apis.data.go.kr')
    SERVICE_URL = getattr(CONFIG, 'SERVICE_URL', '')
    USE_SERVICE_URL = bool(getattr(CONFIG, 'USE_SERVICE_URL', False))
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
    return str(value).strip()


def item_to_dict(elem):
    data = {}
    for child in list(elem):
        key = child.tag.split('}')[-1]
        if list(child):
            data[key] = item_to_dict(child)
        else:
            data[key] = text(child.text)
    return data


def parse_xml_response(xml_bytes):
    root = ElementTree.fromstring(xml_bytes)

    def find(path):
        return root.find(path)

    result_code = text(find('.//resultCode').text if find('.//resultCode') is not None else '')
    result_msg = text(find('.//resultMsg').text if find('.//resultMsg') is not None else '')
    total_count = int(text(find('.//totalCount').text if find('.//totalCount') is not None else '0') or 0)
    page_no = int(text(find('.//pageNo').text if find('.//pageNo') is not None else '1') or 1)
    num_of_rows = int(text(find('.//numOfRows').text if find('.//numOfRows') is not None else '0') or 0)

    items = []
    for item in root.findall('.//items/item'):
        items.append(item_to_dict(item))

    return {
        'result_code': result_code,
        'result_msg': result_msg,
        'total_count': total_count,
        'page_no': page_no,
        'num_of_rows': num_of_rows,
        'items': items,
    }


def build_url(service_host, endpoint_path, params):
    ensure_config_loaded()
    params = dict(params)
    service_key = str(params.pop('serviceKey', ''))
    query = urlencode(params)
    if service_key:
        query = f'serviceKey={service_key}&{query}' if query else f'serviceKey={service_key}'
    if USE_SERVICE_URL and SERVICE_URL:
        service_name = service_host.rstrip('/').split('/')[-1]
        base_url = f'{SERVICE_URL.rstrip("/")}/{service_name}'
        return f'{base_url}{endpoint_path}?{query}'
    if service_host.startswith('http://') or service_host.startswith('https://'):
        base_url = service_host.rstrip('/')
    elif service_host.startswith('apis.data.go.kr/'):
        base_url = f'https://{service_host.rstrip("/")}'
    else:
        base_url = f'{BASE_API_URL.rstrip("/")}/{service_host.strip("/")}'
    return f'{base_url}{endpoint_path}?{query}'


def fetch_xml(service_host, endpoint_path, params):
    ensure_config_loaded()
    url = build_url(service_host, endpoint_path, params)
    delays = [0, 2, 5]

    for attempt, delay in enumerate(delays, start=1):
        if delay > 0:
            time.sleep(delay)

        try:
            with urlopen(url, timeout=120) as response:
                return url, response.read()
        except HTTPError as exc:
            if exc.code not in (502, 503, 504) or attempt == len(delays):
                raise
            log(f'재시도 예정: HTTP {exc.code} {endpoint_path} attempt={attempt}')
        except URLError as exc:
            if attempt == len(delays):
                raise
            log(f'재시도 예정: URL 오류 {endpoint_path} attempt={attempt} error={exc.reason}')


def save_raw(job_name, endpoint_name, page_no, xml_bytes):
    ensure_config_loaded()
    ensure_dir(RAW_DIR)
    target_dir = RAW_DIR / job_name / endpoint_name
    ensure_dir(target_dir)
    file_name = datetime.now().strftime('%Y%m%d-%H%M%S')
    file_path = target_dir / f'{file_name}-p{page_no}.xml'
    file_path.write_bytes(xml_bytes)
    latest_path = target_dir / 'latest.xml'
    latest_path.write_bytes(xml_bytes)
    return file_path


def value_or_default(data, key, default=''):
    return text(data.get(key, default))


def int_or_zero(value):
    value = text(value)
    if value == '':
        return 0
    try:
        return int(float(value.replace(',', '')))
    except ValueError:
        return 0


def first_non_empty(*values):
    for value in values:
        value = text(value)
        if value != '':
            return value
    return ''
