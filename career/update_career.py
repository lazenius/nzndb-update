#!/usr/bin/env python3
import argparse
import os
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from time import sleep
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
import xml.etree.ElementTree as ET

from include import crawler_common as common
from include.crawler_common import connect_db, ensure_dict, ensure_list, float_or_zero, int_or_zero, log, save_raw, text


BASE_DIR = Path(__file__).resolve().parent
COLLECTION_PLAN_PATH = BASE_DIR / 'COLLECTION_PLAN.md'
SYNC_JOB_DETAIL_LOG_NAME = 'sync_job_detail.log'
LEGACY_XML_MAX_ATTEMPTS = 3


CREATE_STATEMENTS = [
    f"""
    CREATE DATABASE IF NOT EXISTS {common.DB_NAME}
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.code_list (
        code char(6) NOT NULL,
        name varchar(100) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.job_list (
        code int unsigned NOT NULL,
        name varchar(100) NOT NULL,
        std_code char(6) NOT NULL default '',
        emp_code char(6) NOT NULL default '',
        apt_code char(6) NOT NULL default '',
        thm_code char(6) NOT NULL default '',
        cat_code char(6) NOT NULL default '',
        related_job varchar(300) NOT NULL default '',
        social varchar(30) NOT NULL default '',
        balance varchar(30) NOT NULL default '',
        satisfication decimal(4,1) unsigned NOT NULL default 0,
        wage int unsigned NOT NULL default 0,
        edit_date varchar(20) NOT NULL default '',
        reg_date varchar(20) NOT NULL default '',
        views int unsigned NOT NULL default 0,
        likes int unsigned NOT NULL default 0,
        tag varchar(300) NOT NULL default '',
        recv_time datetime NOT NULL,
        PRIMARY KEY (code),
        KEY name_idx (name),
        KEY apt_code_idx (apt_code),
        KEY thm_code_idx (thm_code),
        KEY cat_code_idx (cat_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.school_list (
        school char(4) NOT NULL,
        seq int unsigned NOT NULL,
        name varchar(50) NOT NULL default '',
        campus varchar(50) NOT NULL default '',
        sch1 char(6) NOT NULL default '',
        sch2 char(6) NOT NULL default '',
        region char(6) NOT NULL default '',
        est char(6) NOT NULL default '',
        address varchar(200) NOT NULL default '',
        link varchar(300) NOT NULL default '',
        info varchar(300) NOT NULL default '',
        recv_time datetime NOT NULL,
        PRIMARY KEY (school, seq),
        KEY name_idx (name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.subject_list (
        school char(4) NOT NULL,
        seq int unsigned NOT NULL,
        name varchar(30) NOT NULL default '',
        faculty char(6) NOT NULL default '',
        others varchar(3000) NOT NULL default '',
        recv_time datetime NOT NULL,
        PRIMARY KEY (school, seq),
        KEY name_idx (name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.job_work_list (
        jcode int unsigned NOT NULL,
        seq tinyint unsigned NOT NULL,
        work varchar(1000) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (jcode, seq)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.interest_list (
        jcode int unsigned NOT NULL,
        seq tinyint unsigned NOT NULL,
        interest varchar(3000) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (jcode, seq)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.research_list (
        jcode int unsigned NOT NULL,
        seq tinyint unsigned NOT NULL,
        research varchar(3000) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (jcode, seq)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.job_ready_list (
        jcode int unsigned NOT NULL,
        recruit varchar(3000) NOT NULL,
        certificate varchar(3000) NOT NULL,
        training varchar(3000) NOT NULL,
        curriculum varchar(3000) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (jcode)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.forecast_list (
        jcode int unsigned NOT NULL,
        forecast varchar(3000) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (jcode)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.perform_list (
        jcode int unsigned NOT NULL,
        area enum('environment','perform','knowledge') NOT NULL,
        seq tinyint unsigned NOT NULL,
        name varchar(100) NOT NULL,
        inform varchar(1000) NOT NULL,
        importance tinyint unsigned NOT NULL,
        source varchar(300) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (jcode, area, seq),
        KEY name_idx (name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.ability_list (
        jcode int unsigned NOT NULL,
        sort_ordr char(2) NOT NULL,
        ability_name varchar(100) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (jcode, sort_ordr),
        KEY ability_name_idx (ability_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.depart_list (
        jcode int unsigned NOT NULL,
        depart_id int unsigned NOT NULL,
        depart_name varchar(100) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (jcode, depart_id),
        KEY depart_name_idx (depart_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.tag_list (
        jcode int unsigned NOT NULL,
        seq tinyint unsigned NOT NULL,
        tag varchar(100) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (jcode, seq),
        KEY tag_idx (tag)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.job_rel_org_list (
        jcode int unsigned NOT NULL,
        seq tinyint unsigned NOT NULL,
        rel_org varchar(100) NOT NULL,
        rel_org_url varchar(300) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (jcode, seq)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.subject_detail_list (
        school char(4) NOT NULL,
        seq int unsigned NOT NULL,
        name varchar(100) NOT NULL,
        salary varchar(50) NOT NULL,
        employment varchar(50) NOT NULL,
        department text NOT NULL,
        summary text NOT NULL,
        job text NOT NULL,
        qualifications text NOT NULL,
        interest text NOT NULL,
        property text NOT NULL,
        purpose text NOT NULL,
        relatedjob text NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (school, seq)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.subject_text_list (
        school char(4) NOT NULL,
        seq int unsigned NOT NULL,
        section varchar(30) NOT NULL,
        item_seq smallint unsigned NOT NULL,
        item_name varchar(100) NOT NULL,
        item_desc text NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (school, seq, section, item_seq)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.subject_school_map (
        school char(4) NOT NULL,
        seq int unsigned NOT NULL,
        item_seq smallint unsigned NOT NULL,
        school_name varchar(100) NOT NULL,
        area varchar(50) NOT NULL,
        school_url varchar(300) NOT NULL,
        campus varchar(50) NOT NULL,
        major_name varchar(100) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (school, seq, item_seq),
        KEY school_name_idx (school_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.subject_chart_list (
        school char(4) NOT NULL,
        seq int unsigned NOT NULL,
        chart_type varchar(30) NOT NULL,
        item_seq smallint unsigned NOT NULL,
        item_name varchar(100) NOT NULL,
        item_label varchar(100) NOT NULL,
        item_value varchar(50) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (school, seq, chart_type, item_seq)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.subject_feature_list (
        school char(4) NOT NULL,
        seq int unsigned NOT NULL,
        feature_group varchar(30) NOT NULL,
        feature_type varchar(20) NOT NULL,
        item_seq smallint unsigned NOT NULL,
        item_name varchar(100) NOT NULL,
        rank_no varchar(10) NOT NULL,
        order_no varchar(10) NOT NULL,
        pct varchar(20) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (school, seq, feature_group, feature_type, item_seq)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.aptitude_test_list (
        version varchar(10) NOT NULL,
        qno int unsigned NOT NULL,
        name varchar(100) NOT NULL,
        target varchar(50) NOT NULL,
        summary text NOT NULL,
        question_count smallint unsigned NOT NULL default 0,
        recv_time datetime NOT NULL,
        PRIMARY KEY (version, qno)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.aptitude_question_list (
        version varchar(10) NOT NULL,
        qno int unsigned NOT NULL,
        question_no int unsigned NOT NULL,
        title varchar(300) NOT NULL,
        question_text text NOT NULL,
        choice_limit smallint unsigned NOT NULL default 0,
        recv_time datetime NOT NULL,
        PRIMARY KEY (version, qno, question_no)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.aptitude_choice_list (
        version varchar(10) NOT NULL,
        qno int unsigned NOT NULL,
        question_no int unsigned NOT NULL,
        choice_no smallint unsigned NOT NULL,
        choice_value varchar(50) NOT NULL,
        choice_text varchar(300) NOT NULL,
        choice_type varchar(10) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (version, qno, question_no, choice_no)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
]


CODE_ENDPOINTS = [
    ('themes', 'themes'),
    ('aptds', 'aptds'),
    ('jobcodes', 'jobcodes'),
]


SCHOOL_GUBUNS = [
    ('elem_list', 'elem'),
    ('midd_list', 'midd'),
    ('high_list', 'high'),
    ('univ_list', 'univ'),
    ('seet_list', 'seet'),
    ('alte_list', 'alte'),
]


SUBJECT_GUBUNS = [
    ('high_list', 'high'),
    ('univ_list', 'univ'),
]


APTITUDE_V2_TESTS_PATH = '/inspct/openapi/v2/tests'
APTITUDE_V2_TEST_PATH = '/inspct/openapi/v2/test'


REGION_CODE_BY_NAME = {
    '서울특별시': '100260',
    '부산광역시': '100267',
    '인천광역시': '100269',
    '대전광역시': '100271',
    '대구광역시': '100272',
    '울산광역시': '100273',
    '광주광역시': '100275',
    '경기도': '100276',
    '강원특별자치도': '100278',
    '충청북도': '100280',
    '충청남도': '100281',
    '전북특별자치도': '100282',
    '전라남도': '100283',
    '경상북도': '100285',
    '경상남도': '100291',
    '제주도': '100292',
}


SCHOOL_GUBUN1_CODE_BY_NAME = {
    '일반고': '100362',
    '특성화고': '100363',
    '특수목적고': '100364',
    '자율고': '100365',
    '기타': '100366',
    '전문대학': '100322',
    '대학(4년제)': '100323',
}


SCHOOL_GUBUN2_CODE_BY_NAME = {
    '일반고': '104228',
    '대안교육': '100368',
    '직업교육': '100369',
    '기타': '100370',
    '과학계열': '100371',
    '외국어국제계열': '100372',
    '예술체육계열': '100373',
    '마이스터고': '100374',
    '자율형사립': '100375',
    '자율형공립': '100376',
    '영재학교': '100377',
    '전문대학': '100324',
    '기능대학': '100325',
    '사이버대학(2년제)': '100326',
    '각종대학(전문)': '100327',
    '일반대학': '100328',
    '교육대학': '100329',
    '산업대학': '100330',
    '사이버대학(대학)': '100331',
    '각종대학(대학)': '100332',
}


EST_CODE_BY_NAME = {
    '국립': '100334',
    '사립': '100335',
    '공립': '100336',
}


FACULTY_CODE_BY_NAME = {
    '인문계열': '100391',
    '사회계열': '100392',
    '교육계열': '100393',
    '공학계열': '100394',
    '자연계열': '100395',
    '의약계열': '100396',
    '예체능계열': '100397',
}


def first_text(*values):
    for value in values:
        value = text(value)
        if value != '':
            return value
    return ''


def first_data(*values):
    for value in values:
        if value is None:
            continue
        if isinstance(value, (list, tuple, dict)):
            if value:
                return value
            continue
        if text(value) != '':
            return value
    return None


def split_csv(value):
    return [text(x) for x in text(value).split(',') if text(x) != '']


def extract_content_list(payload, *keys):
    payload = ensure_dict(payload)
    for key in keys:
        content = payload.get(key)
        if isinstance(content, list):
            return content
        if isinstance(content, dict):
            return [content]
    data_search = ensure_dict(payload.get('dataSearch'))
    content = data_search.get('content')
    if isinstance(content, list):
        return content
    if isinstance(content, dict):
        return [content]
    return []


def extract_detail_row(payload):
    payload = ensure_dict(payload)
    if isinstance(payload.get('baseInfo'), dict):
        return payload
    rows = extract_content_list(payload, 'jobs', 'content')
    if rows:
        return ensure_dict(rows[0])
    return {}


def normalized_items(value):
    items = []
    for item in ensure_list(value):
        if isinstance(item, dict):
            items.append(item)
            continue
        item_value = text(item)
        if item_value != '':
            items.append({'value': item_value})
    return items


def item_texts(value):
    result = []
    for row in normalized_items(value):
        item_value = first_text(
            row.get('work'),
            row.get('interest'),
            row.get('research'),
            row.get('value'),
            row.get('name'),
            row.get('txt'),
            row.get('content'),
            row.get('desc'),
            row.get('summary'),
        )
        if item_value != '':
            result.append(item_value)
    return result


def ensure_tables():
    conn = connect_db(autocommit=True)
    try:
        with conn.cursor() as cur:
            for statement in CREATE_STATEMENTS:
                cur.execute(statement)
    finally:
        conn.close()


class TeeStream:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
        return len(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()


def stream_points_to_path(stream, target_path):
    fileno = getattr(stream, 'fileno', None)
    if fileno is None:
        return False
    try:
        fd_no = fileno()
    except OSError:
        return False

    for probe_path in (f'/proc/self/fd/{fd_no}', f'/dev/fd/{fd_no}'):
        try:
            resolved = os.path.realpath(probe_path)
        except OSError:
            continue
        if resolved == str(target_path):
            return True
    return False


@contextmanager
def append_job_detail_log():
    common.ensure_config_loaded()
    common.ensure_dir(common.LOG_DIR)
    target_path = Path(common.LOG_DIR) / SYNC_JOB_DETAIL_LOG_NAME
    needs_stdout_tee = not stream_points_to_path(sys.stdout, target_path)
    needs_stderr_tee = not stream_points_to_path(sys.stderr, target_path)
    if not needs_stdout_tee and not needs_stderr_tee:
        yield
        return

    with target_path.open('a', encoding='utf-8') as fp:
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = TeeStream(original_stdout, fp) if needs_stdout_tee else original_stdout
        sys.stderr = TeeStream(original_stderr, fp) if needs_stderr_tee else original_stderr
        try:
            yield
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = original_stdout
            sys.stderr = original_stderr


def print_plan():
    print(COLLECTION_PLAN_PATH.read_text(), end='')


def build_legacy_xml_url(params):
    common.ensure_config_loaded()
    merged = {
        'apiKey': common.API_KEY,
        'svcType': 'api',
        'contentType': 'xml',
    }
    merged.update(params)
    return f'{common.BASE_API_URL}/cnet/openapi/getOpenApi?{urlencode(merged)}'


def fetch_legacy_xml(params):
    url = build_legacy_xml_url(params)
    for attempt in range(1, LEGACY_XML_MAX_ATTEMPTS + 1):
        try:
            with urlopen(url, timeout=120) as response:
                payload = response.read().decode('utf-8')
            return url, payload
        except HTTPError as exc:
            if not 500 <= exc.code < 600 or attempt == LEGACY_XML_MAX_ATTEMPTS:
                raise
            log(
                f'HTTP {exc.code} 응답, {attempt}초 후 재시도 '
                f'({attempt}/{LEGACY_XML_MAX_ATTEMPTS - 1}): {common.safe_url(url)}'
            )
            sleep(attempt)


def parse_xml_contents(payload):
    root = ET.fromstring(payload)
    return root.findall('.//content')


def xml_text(node, name):
    child = node.find(name)
    if child is None or child.text is None:
        return ''
    return text(child.text)


def xml_child(node, name):
    child = node.find(name)
    if child is None:
        return None
    return child


def xml_contents(node, name):
    child = xml_child(node, name)
    if child is None:
        return []
    return child.findall('content')


def build_aptitude_url(path, params=None):
    common.ensure_config_loaded()
    query = {'apikey': common.API_KEY}
    if params:
        query.update(params)
    return f'{common.BASE_API_URL}{path}?{urlencode(query)}'


def fetch_aptitude_json(path, params=None):
    url = build_aptitude_url(path, params)
    payload = json.loads(common.fetch_json_url(url).decode('utf-8'))
    return url, payload


def aptitude_result_list(payload):
    payload = ensure_dict(payload)
    result = payload.get('result')
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return [result]
    result = payload.get('RESULT')
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return [result]
    return []


def aptitude_result_dict(payload):
    rows = aptitude_result_list(payload)
    if rows:
        return ensure_dict(rows[0])
    payload = ensure_dict(payload)
    return ensure_dict(payload.get('result') or payload.get('RESULT'))


def upsert_code_rows(rows):
    conn = connect_db(common.DB_NAME)
    try:
        with conn.cursor() as cur:
            for row in rows:
                code = first_text(row.get('code'), row.get('job_cd'), row.get('jobCode'))[:6]
                name = first_text(row.get('name'), row.get('job'), row.get('nm'), row.get('codeNm'), row.get('value'))
                if code == '' or name == '':
                    continue
                cur.execute(
                    f"""
                    INSERT INTO {common.DB_NAME}.code_list (code, name, recv_time)
                    VALUES (%s, %s, NOW())
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name),
                        recv_time = VALUES(recv_time)
                    """,
                    (code, name),
                )
        conn.commit()
    finally:
        conn.close()


def upsert_school_rows(gubun, school_key, nodes):
    conn = connect_db(common.DB_NAME)
    try:
        with conn.cursor() as cur:
            for node in nodes:
                campus = xml_text(node, 'campusName') if gubun == 'univ_list' else ''
                info = xml_text(node, 'collegeinfourl') if gubun == 'univ_list' else ''
                sch1 = ''
                sch2 = ''
                if gubun in ('univ_list', 'high_list'):
                    sch1 = SCHOOL_GUBUN1_CODE_BY_NAME.get(xml_text(node, 'schoolGubun'), xml_text(node, 'schoolGubun'))[:6]
                    sch2 = SCHOOL_GUBUN2_CODE_BY_NAME.get(xml_text(node, 'schoolType'), xml_text(node, 'schoolType'))[:6]

                cur.execute(
                    f"""
                    INSERT INTO {common.DB_NAME}.school_list (
                        school, seq, name, campus, sch1, sch2, region, est, address, link, info, recv_time
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name),
                        campus=VALUES(campus),
                        sch1=VALUES(sch1),
                        sch2=VALUES(sch2),
                        region=VALUES(region),
                        est=VALUES(est),
                        address=VALUES(address),
                        link=VALUES(link),
                        info=VALUES(info),
                        recv_time=VALUES(recv_time)
                    """,
                    (
                        school_key,
                        int_or_zero(xml_text(node, 'seq')),
                        xml_text(node, 'schoolName')[:50],
                        campus[:50],
                        sch1,
                        sch2,
                        REGION_CODE_BY_NAME.get(xml_text(node, 'region'), xml_text(node, 'region'))[:6],
                        EST_CODE_BY_NAME.get(xml_text(node, 'estType'), xml_text(node, 'estType'))[:6],
                        xml_text(node, 'adres')[:200],
                        xml_text(node, 'link')[:300],
                        info[:300],
                    ),
                )
        conn.commit()
    finally:
        conn.close()


def sync_school_list():
    ensure_tables()
    total = 0
    for gubun, school_key in SCHOOL_GUBUNS:
        url, payload = fetch_legacy_xml({
            'svcCode': 'SCHOOL',
            'gubun': gubun,
            'thisPage': 1,
            'perPage': 10000,
            'region': '',
            'sch1': '',
            'sch2': '',
            'est': '',
        })
        save_raw('sync_school_list', f'{school_key}.xml', {'url': common.safe_url(url), 'xml': payload})
        nodes = parse_xml_contents(payload)
        upsert_school_rows(gubun, school_key, nodes)
        total += len(nodes)
        log(f'{gubun}: {len(nodes)}건 적재 ({common.safe_url(url)})')
    log(f'school_list 동기화 완료: 총 {total}건')


def upsert_subject_rows(school_key, nodes):
    conn = connect_db(common.DB_NAME)
    try:
        with conn.cursor() as cur:
            for node in nodes:
                cur.execute(
                    f"""
                    INSERT INTO {common.DB_NAME}.subject_list (
                        school, seq, name, faculty, others, recv_time
                    ) VALUES (%s, %s, %s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name),
                        faculty=VALUES(faculty),
                        others=VALUES(others),
                        recv_time=VALUES(recv_time)
                    """,
                    (
                        school_key,
                        int_or_zero(xml_text(node, 'majorSeq')),
                        xml_text(node, 'mClass')[:30],
                        FACULTY_CODE_BY_NAME.get(xml_text(node, 'lClass'), xml_text(node, 'lClass'))[:6],
                        xml_text(node, 'facilName')[:3000],
                    ),
                )
        conn.commit()
    finally:
        conn.close()


def sync_subject_list():
    ensure_tables()
    total = 0
    for gubun, school_key in SUBJECT_GUBUNS:
        url, payload = fetch_legacy_xml({
            'svcCode': 'MAJOR',
            'gubun': gubun,
            'subject': '',
            'thisPage': 1,
            'perPage': 1000,
        })
        save_raw('sync_subject_list', f'{school_key}.xml', {'url': common.safe_url(url), 'xml': payload})
        nodes = parse_xml_contents(payload)
        upsert_subject_rows(school_key, nodes)
        total += len(nodes)
        log(f'{gubun}: {len(nodes)}건 적재 ({common.safe_url(url)})')
    log(f'subject_list 동기화 완료: 총 {total}건')


def load_subject_rows(cur, school='', limit=0):
    sql = f'SELECT school, seq FROM {common.DB_NAME}.subject_list'
    params = []
    if school:
        sql += ' WHERE school = %s'
        params.append(school)
    sql += ' ORDER BY school, seq'
    if limit > 0:
        sql += ' LIMIT %s'
        params.append(limit)
    cur.execute(sql, params)
    return cur.fetchall()


def fetch_subject_detail(school_key, seq):
    params = {
        'svcCode': 'MAJOR_VIEW',
        'gubun': f'{school_key}_list',
        'majorSeq': seq,
        'thisPage': 1,
        'perPage': 1000,
    }
    return fetch_legacy_xml(params)


def delete_subject_detail_rows(cur, table_name, school_key, seq):
    cur.execute(f'DELETE FROM {common.DB_NAME}.{table_name} WHERE school = %s AND seq = %s', (school_key, seq))


def replace_subject_detail(cur, school_key, seq, node):
    delete_subject_detail_rows(cur, 'subject_detail_list', school_key, seq)
    cur.execute(
        f"""
        INSERT INTO {common.DB_NAME}.subject_detail_list (
            school, seq, name, salary, employment, department, summary,
            job, qualifications, interest, property, purpose, relatedjob, recv_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """,
        (
            school_key,
            seq,
            first_text(xml_text(node, 'major'), xml_text(node, 'majorName'))[:100],
            xml_text(node, 'salary')[:50],
            xml_text(node, 'employment')[:50],
            xml_text(node, 'department'),
            xml_text(node, 'summary'),
            xml_text(node, 'job'),
            xml_text(node, 'qualifications'),
            xml_text(node, 'interest'),
            xml_text(node, 'property'),
            xml_text(node, 'purpose'),
            first_text(xml_text(node, 'relatedjob'), xml_text(node, 'relatedjob ')),
        ),
    )


def replace_subject_text_rows(cur, school_key, seq, section, rows, name_key, desc_key):
    cur.execute(
        f'DELETE FROM {common.DB_NAME}.subject_text_list WHERE school = %s AND seq = %s AND section = %s',
        (school_key, seq, section),
    )
    for idx, row in enumerate(rows, start=1):
        name = first_text(xml_text(row, name_key), xml_text(row, 'name'), xml_text(row, 'item'))
        desc = first_text(xml_text(row, desc_key), xml_text(row, 'description'), xml_text(row, 'desc'), xml_text(row, 'summary'))
        if name == '' and desc == '':
            continue
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.subject_text_list (
                school, seq, section, item_seq, item_name, item_desc, recv_time
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (school_key, seq, section, idx, name[:100], desc),
        )


def replace_subject_school_rows(cur, school_key, seq, rows):
    delete_subject_detail_rows(cur, 'subject_school_map', school_key, seq)
    for idx, row in enumerate(rows, start=1):
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.subject_school_map (
                school, seq, item_seq, school_name, area, school_url, campus, major_name, recv_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                school_key,
                seq,
                idx,
                xml_text(row, 'schoolName')[:100],
                xml_text(row, 'area')[:50],
                xml_text(row, 'schoolURL')[:300],
                xml_text(row, 'campus_nm')[:50],
                xml_text(row, 'majorName')[:100],
            ),
        )


def replace_subject_chart_rows(cur, school_key, seq, chart_type, rows):
    cur.execute(
        f'DELETE FROM {common.DB_NAME}.subject_chart_list WHERE school = %s AND seq = %s AND chart_type = %s',
        (school_key, seq, chart_type),
    )
    for idx, row in enumerate(rows, start=1):
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.subject_chart_list (
                school, seq, chart_type, item_seq, item_name, item_label, item_value, recv_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                school_key,
                seq,
                chart_type,
                idx,
                first_text(xml_text(row, 'item'), xml_text(row, 'IEM'))[:100],
                first_text(xml_text(row, 'name'), xml_text(row, 'NM'))[:100],
                first_text(xml_text(row, 'data'), xml_text(row, 'DATA'))[:50],
            ),
        )


def replace_subject_feature_rows(cur, school_key, seq, feature_group, feature_type, rows):
    cur.execute(
        f"""
        DELETE FROM {common.DB_NAME}.subject_feature_list
        WHERE school = %s AND seq = %s AND feature_group = %s AND feature_type = %s
        """,
        (school_key, seq, feature_group, feature_type),
    )
    for idx, row in enumerate(rows, start=1):
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.subject_feature_list (
                school, seq, feature_group, feature_type, item_seq, item_name, rank_no, order_no, pct, recv_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                school_key,
                seq,
                feature_group,
                feature_type,
                idx,
                first_text(xml_text(row, 'GEN_NM'), xml_text(row, 'SCH_CLASS_NM'), xml_text(row, 'CD_NM'))[:100],
                xml_text(row, 'RANK')[:10],
                xml_text(row, 'CD_ORDR')[:10],
                xml_text(row, 'PCNT')[:20],
            ),
        )


def sync_subject_detail(school='', seq=0, limit=0):
    if seq > 0 and school == '':
        raise ValueError('subject 상세 단건 수집 시 --school 은 필수입니다')
    ensure_tables()
    conn = connect_db(common.DB_NAME)
    try:
        with conn.cursor() as cur:
            if seq > 0:
                targets = [{'school': school, 'seq': seq}]
            else:
                targets = load_subject_rows(cur, school=school, limit=limit)

            for row in targets:
                school_key = text(row['school'])
                subject_seq = int_or_zero(row['seq'])
                url, payload = fetch_subject_detail(school_key, subject_seq)
                save_raw(
                    'sync_subject_detail',
                    f'{school_key}-{subject_seq}.json',
                    {'url': common.safe_url(url), 'xml': payload},
                )
                nodes = parse_xml_contents(payload)
                if not nodes:
                    log(f'subject {school_key}/{subject_seq}: 상세 데이터 없음 ({common.safe_url(url)})')
                    continue
                node = nodes[0]
                replace_subject_detail(cur, school_key, subject_seq, node)
                replace_subject_text_rows(cur, school_key, subject_seq, 'relate_subject', xml_contents(node, 'relate_subject'), 'subject_name', 'subject_description')
                replace_subject_text_rows(cur, school_key, subject_seq, 'career_act', xml_contents(node, 'career_act'), 'act_name', 'act_description')
                replace_subject_text_rows(cur, school_key, subject_seq, 'enter_field', xml_contents(node, 'enter_field'), 'gradeuate', 'description')
                replace_subject_text_rows(cur, school_key, subject_seq, 'main_subject', xml_contents(node, 'main_subject'), 'SBJECT_NM', 'SBJECT_SUMRY')

                school_rows = xml_contents(node, 'setshl')
                if not school_rows:
                    school_rows = xml_contents(node, 'university')
                replace_subject_school_rows(cur, school_key, subject_seq, school_rows)

                chart_data = xml_child(node, 'chartData')
                if chart_data is not None:
                    for chart_type in ('applicant', 'gender', 'employment_rate', 'field', 'avg_salary', 'satisfaction', 'after_graduation'):
                        replace_subject_chart_rows(cur, school_key, subject_seq, chart_type, xml_contents(chart_data, chart_type))
                replace_subject_chart_rows(cur, school_key, subject_seq, 'graduation_gender', xml_contents(node, 'graduation_gender'))

                for feature_group in ('GenCD', 'SchClass', 'lstMiddleAptd', 'lstHighAptd', 'lstVals'):
                    group_node = xml_child(node, feature_group)
                    if group_node is None:
                        replace_subject_feature_rows(cur, school_key, subject_seq, feature_group, 'popular', [])
                        replace_subject_feature_rows(cur, school_key, subject_seq, feature_group, 'bookmark', [])
                        continue
                    replace_subject_feature_rows(cur, school_key, subject_seq, feature_group, 'popular', xml_contents(group_node, 'popular'))
                    replace_subject_feature_rows(cur, school_key, subject_seq, feature_group, 'bookmark', xml_contents(group_node, 'bookmark'))

                log(f'subject {school_key}/{subject_seq}: 상세 동기화 완료 ({common.safe_url(url)})')
        conn.commit()
    finally:
        conn.close()


def upsert_aptitude_test(cur, version, row, question_count):
    qno = int_or_zero(first_text(row.get('qno'), row.get('qestnrSeq')))
    if qno == 0:
        return 0
    cur.execute(
        f"""
        INSERT INTO {common.DB_NAME}.aptitude_test_list (
            version, qno, name, target, summary, question_count, recv_time
        ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            name=VALUES(name),
            target=VALUES(target),
            summary=VALUES(summary),
            question_count=VALUES(question_count),
            recv_time=VALUES(recv_time)
        """,
        (
            version,
            qno,
            first_text(row.get('name'), row.get('qnm'))[:100],
            first_text(row.get('target'), row.get('grade'), row.get('school'))[:50],
            first_text(row.get('summary'), row.get('info'), row.get('description')),
            question_count,
        ),
    )
    return qno


def replace_aptitude_questions(cur, version, qno, questions):
    cur.execute(
        f'DELETE FROM {common.DB_NAME}.aptitude_question_list WHERE version = %s AND qno = %s',
        (version, qno),
    )
    cur.execute(
        f'DELETE FROM {common.DB_NAME}.aptitude_choice_list WHERE version = %s AND qno = %s',
        (version, qno),
    )
    for question in questions:
        question_no = int_or_zero(first_text(question.get('no'), question.get('questionNo')))
        if question_no == 0:
            continue
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.aptitude_question_list (
                version, qno, question_no, title, question_text, choice_limit, recv_time
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                version,
                qno,
                question_no,
                first_text(question.get('title'))[:300],
                first_text(question.get('text'), question.get('question')),
                int_or_zero(first_text(question.get('limit'), question.get('choiceLimit'))),
            ),
        )
        for idx, choice in enumerate(ensure_list(question.get('choices')), start=1):
            choice = ensure_dict(choice)
            cur.execute(
                f"""
                INSERT INTO {common.DB_NAME}.aptitude_choice_list (
                    version, qno, question_no, choice_no, choice_value, choice_text, choice_type, recv_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    version,
                    qno,
                    question_no,
                    idx,
                    first_text(choice.get('val'), choice.get('value'))[:50],
                    first_text(choice.get('text'), choice.get('label'))[:300],
                    first_text(choice.get('type'))[:10],
                ),
            )


def fetch_aptitude_v2_tests():
    return fetch_aptitude_json(APTITUDE_V2_TESTS_PATH)


def fetch_aptitude_v2_test(qno):
    return fetch_aptitude_json(APTITUDE_V2_TEST_PATH, {'q': qno})


def sync_aptitude_meta():
    ensure_tables()
    conn = connect_db(common.DB_NAME)
    try:
        with conn.cursor() as cur:
            url, payload = fetch_aptitude_v2_tests()
            save_raw('sync_aptitude_meta', 'v2-tests.json', payload)
            tests = aptitude_result_list(payload)
            total = 0
            for row in tests:
                qno = int_or_zero(first_text(row.get('qno')))
                if qno == 0:
                    continue
                detail_url, detail_payload = fetch_aptitude_v2_test(qno)
                save_raw('sync_aptitude_meta', f'v2-test-{qno}.json', detail_payload)
                detail = aptitude_result_dict(detail_payload)
                questions = ensure_list(detail.get('questions'))
                upsert_aptitude_test(cur, 'v2', {
                    'qno': qno,
                    'name': first_text(detail.get('qnm'), row.get('name')),
                    'target': first_text(row.get('target'), row.get('grade')),
                    'summary': first_text(detail.get('summary')),
                }, len(questions))
                replace_aptitude_questions(cur, 'v2', qno, questions)
                total += 1
                log(f'aptitude v2 {qno}: 문항 {len(questions)}건 동기화 ({common.safe_url(detail_url)})')
        conn.commit()
    finally:
        conn.close()
    log(f'aptitude meta 동기화 완료: 총 {total}건 ({common.safe_url(url)})')


def sync_code_list():
    ensure_tables()
    total = 0
    for endpoint_name, path in CODE_ENDPOINTS:
        url, payload = common.fetch_front_json(path)
        save_raw('sync_code_list', f'{endpoint_name}.json', payload)
        rows = extract_content_list(payload, endpoint_name, path, 'jobs')
        upsert_code_rows(rows)
        total += len(rows)
        log(f'{endpoint_name}: {len(rows)}건 ({common.safe_url(url)})')
    log(f'code_list 동기화 완료: 총 {total}건')


def list_job_rows(page, keyword=''):
    params = {'pageIndex': page}
    if keyword:
        params['searchJobNm'] = keyword
    try:
        return common.fetch_front_json('jobs', params)
    except Exception:
        return common.fetch_legacy_json({
            'svcCode': 'JOB',
            'gubun': 'job_dic_list',
            'pageIndex': page,
            'searchJobNm': keyword,
        })


def parse_job_code(row):
    return int_or_zero(first_text(row.get('job_cd'), row.get('jobdicSeq'), row.get('seq'), row.get('jobCd')))


def upsert_job_list(rows):
    conn = connect_db(common.DB_NAME)
    try:
        with conn.cursor() as cur:
            for row in rows:
                code = parse_job_code(row)
                name = first_text(row.get('job_nm'), row.get('job'), row.get('name'))
                if code == 0 or name == '':
                    continue
                cur.execute(
                    f"""
                    INSERT INTO {common.DB_NAME}.job_list (
                        code, name, std_code, emp_code, apt_code, thm_code, cat_code,
                        related_job, social, balance, satisfication, wage,
                        edit_date, reg_date, views, likes, tag, recv_time
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, NOW()
                    )
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name),
                        std_code = VALUES(std_code),
                        emp_code = VALUES(emp_code),
                        apt_code = VALUES(apt_code),
                        thm_code = VALUES(thm_code),
                        cat_code = VALUES(cat_code),
                        related_job = VALUES(related_job),
                        social = VALUES(social),
                        balance = VALUES(balance),
                        satisfication = VALUES(satisfication),
                        wage = VALUES(wage),
                        edit_date = VALUES(edit_date),
                        reg_date = VALUES(reg_date),
                        views = VALUES(views),
                        likes = VALUES(likes),
                        tag = VALUES(tag),
                        recv_time = VALUES(recv_time)
                    """,
                    (
                        code,
                        name,
                        text(row.get('std_code'))[:6],
                        text(row.get('emp_code'))[:6],
                        text(row.get('apt_code'))[:6],
                        text(row.get('thm_code'))[:6],
                        text(row.get('cat_code'))[:6],
                        first_text(row.get('related_job'), row.get('similarJob')),
                        first_text(row.get('social'), row.get('equalemployment')),
                        first_text(row.get('balance'), row.get('possibility')),
                        float_or_zero(first_text(row.get('satisfication'), row.get('satisfaction'))),
                        int_or_zero(first_text(row.get('wage'), row.get('salery'))),
                        text(row.get('edit_date')),
                        text(row.get('reg_date')),
                        int_or_zero(row.get('views')),
                        int_or_zero(row.get('likes')),
                        text(row.get('tag')),
                    ),
                )
        conn.commit()
    finally:
        conn.close()


def sync_job_list(keyword='', max_pages=0):
    ensure_tables()
    total = 0
    page = 1
    while True:
        url, payload = list_job_rows(page, keyword)
        save_raw('sync_job_list', f'page-{page}.json', payload)
        rows = extract_content_list(payload, 'jobs')
        if not rows:
            log(f'page {page}: 데이터 없음 ({common.safe_url(url)})')
            break
        upsert_job_list(rows)
        total += len(rows)
        log(f'page {page}: {len(rows)}건 적재 ({common.safe_url(url)})')
        if max_pages > 0 and page >= max_pages:
            break
        page += 1
    log(f'job_list 동기화 완료: 총 {total}건')


def fetch_job_detail(seq):
    try:
        return common.fetch_front_json('job', {'seq': seq})
    except Exception:
        return common.fetch_legacy_json({
            'svcCode': 'JOB_VIEW',
            'gubun': 'job_dic_list',
            'jobdicSeq': seq,
        })


def replace_detail_rows(cur, table_name, jcode):
    cur.execute(f'DELETE FROM {common.DB_NAME}.{table_name} WHERE jcode = %s', (jcode,))


def replace_text_table(cur, table_name, column_name, jcode, values):
    replace_detail_rows(cur, table_name, jcode)
    sql = f"INSERT INTO {common.DB_NAME}.{table_name} (jcode, seq, {column_name}, recv_time) VALUES (%s, %s, %s, NOW())"
    for idx, value in enumerate(values, start=1):
        cur.execute(sql, (jcode, idx, value))


def replace_job_ready(cur, jcode, row):
    row = ensure_dict(row)
    cur.execute(f'DELETE FROM {common.DB_NAME}.job_ready_list WHERE jcode = %s', (jcode,))
    cur.execute(
        f"""
        INSERT INTO {common.DB_NAME}.job_ready_list (
            jcode, recruit, certificate, training, curriculum, recv_time
        ) VALUES (%s, %s, %s, %s, %s, NOW())
        """,
        (
            jcode,
            first_text(row.get('recruit'), row.get('empway')),
            first_text(row.get('certificate'), row.get('certificateName')),
            first_text(row.get('training'), row.get('train')),
            first_text(row.get('curriculum'), row.get('curriculumName')),
        ),
    )


def replace_forecast(cur, jcode, forecast):
    cur.execute(f'DELETE FROM {common.DB_NAME}.forecast_list WHERE jcode = %s', (jcode,))
    cur.execute(
        f"""
        INSERT INTO {common.DB_NAME}.forecast_list (jcode, forecast, recv_time)
        VALUES (%s, %s, NOW())
        """,
        (jcode, text(forecast)),
    )


def replace_perform_rows(cur, jcode, area, rows):
    cur.execute(f'DELETE FROM {common.DB_NAME}.perform_list WHERE jcode = %s AND area = %s', (jcode, area))
    for idx, row in enumerate(rows, start=1):
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.perform_list (
                jcode, area, seq, name, inform, importance, source, recv_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                jcode,
                area,
                idx,
                first_text(row.get('name'), row.get('item'), row.get('title')),
                first_text(row.get('inform'), row.get('content'), row.get('desc')),
                int_or_zero(first_text(row.get('importance'), row.get('value'), row.get('score'))),
                first_text(row.get('source'), row.get('src')),
            ),
        )


def replace_ability_rows(cur, jcode, rows):
    replace_detail_rows(cur, 'ability_list', jcode)
    for idx, row in enumerate(rows, start=1):
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.ability_list (jcode, sort_ordr, ability_name, recv_time)
            VALUES (%s, %s, %s, NOW())
            """,
            (jcode, str(idx).zfill(2), first_text(row.get('ability_name'), row.get('ability'), row.get('value'), row.get('name'))),
        )


def replace_depart_rows(cur, jcode, rows):
    replace_detail_rows(cur, 'depart_list', jcode)
    seen_depart_ids = set()
    for idx, row in enumerate(rows, start=1):
        depart_id = int_or_zero(first_text(row.get('depart_id'), row.get('id'), idx))
        if depart_id in seen_depart_ids:
            log(f'job {jcode}: depart_id 중복 스킵 {depart_id}')
            continue
        seen_depart_ids.add(depart_id)
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.depart_list (jcode, depart_id, depart_name, recv_time)
            VALUES (%s, %s, %s, NOW())
            """,
            (jcode, depart_id, first_text(row.get('depart_name'), row.get('name'), row.get('value'))),
        )


def replace_tag_rows(cur, jcode, values):
    replace_detail_rows(cur, 'tag_list', jcode)
    for idx, value in enumerate(values, start=1):
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.tag_list (jcode, seq, tag, recv_time)
            VALUES (%s, %s, %s, NOW())
            """,
            (jcode, idx, value),
        )


def replace_rel_org_rows(cur, jcode, rows):
    replace_detail_rows(cur, 'job_rel_org_list', jcode)
    for idx, row in enumerate(rows, start=1):
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.job_rel_org_list (jcode, seq, rel_org, rel_org_url, recv_time)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (
                jcode,
                idx,
                first_text(row.get('rel_org'), row.get('name'), row.get('orgName')),
                first_text(row.get('rel_org_url'), row.get('url'), row.get('orgUrl')),
            ),
        )


def update_job_list_detail(cur, jcode, row):
    cur.execute(
        f"""
        UPDATE {common.DB_NAME}.job_list
        SET name = %s,
            related_job = %s,
            social = %s,
            balance = %s,
            satisfication = %s,
            wage = %s,
            tag = %s,
            recv_time = NOW()
        WHERE code = %s
        """,
        (
            first_text(row.get('job_nm'), row.get('job'), row.get('name')),
            first_text(row.get('related_job'), row.get('similarJob')),
            first_text(row.get('social'), row.get('equalemployment')),
            first_text(row.get('balance'), row.get('possibility')),
            float_or_zero(first_text(row.get('satisfication'), row.get('satisfaction'))),
            int_or_zero(first_text(row.get('wage'), row.get('salery'), row.get('salary'))),
            text(row.get('tag')),
            jcode,
        ),
    )


def build_job_ready_row(row):
    ready = first_data(row.get('jobReadyList'))
    if isinstance(ready, list):
        ready = ensure_dict(ready[0]) if ready else {}
    ready = ensure_dict(ready)
    state_rows = normalized_items(row.get('stateofemp'))
    if not ready and state_rows:
        ready = {
            'recruit': first_text(*(item.get('empway') for item in state_rows)),
            'training': first_text(*(item.get('employment') for item in state_rows)),
        }
    return ready


def sync_job_detail(seq=0, limit=0):
    ensure_tables()
    conn = connect_db(common.DB_NAME)
    try:
        with conn.cursor() as cur:
            if seq > 0:
                target_codes = [seq]
            else:
                sql = f'SELECT code FROM {common.DB_NAME}.job_list ORDER BY code'
                if limit > 0:
                    sql += ' LIMIT %s'
                    cur.execute(sql, (limit,))
                else:
                    cur.execute(sql)
                target_codes = [row['code'] for row in cur.fetchall()]

            for jcode in target_codes:
                url, payload = fetch_job_detail(jcode)
                save_raw('sync_job_detail', f'{jcode}.json', payload)
                row = extract_detail_row(payload)
                if not row:
                    log(f'job {jcode}: 상세 데이터 없음 ({common.safe_url(url)})')
                    continue
                base_row = ensure_dict(row.get('baseInfo')) or row
                update_job_list_detail(cur, jcode, base_row)
                replace_text_table(cur, 'job_work_list', 'work', jcode, item_texts(first_data(row.get('jobWork'), row.get('workList'), row.get('job_work'), row.get('work'))))
                replace_text_table(cur, 'interest_list', 'interest', jcode, item_texts(first_data(row.get('interestList'), row.get('interest'))))
                replace_text_table(cur, 'research_list', 'research', jcode, item_texts(first_data(row.get('researchList'), row.get('research'))))
                replace_job_ready(cur, jcode, build_job_ready_row(row))
                replace_forecast(cur, jcode, first_text(row.get('forecast'), row.get('prospect'), ensure_dict(first_data(row.get('forecastList'))).get('forecast')))
                perform_rows = normalized_items(first_data(row.get('performList')))
                replace_perform_rows(cur, jcode, 'environment', [r for r in perform_rows if first_text(r.get('gbn'), r.get('type')) in ['', 'environment']])
                replace_perform_rows(cur, jcode, 'perform', [r for r in perform_rows if first_text(r.get('gbn'), r.get('type')) == 'perform'])
                replace_perform_rows(cur, jcode, 'knowledge', [r for r in perform_rows if first_text(r.get('gbn'), r.get('type')) == 'knowledge'])
                replace_ability_rows(cur, jcode, normalized_items(first_data(row.get('abilityList'), row.get('ability'))))
                replace_depart_rows(cur, jcode, normalized_items(first_data(row.get('departList'), row.get('depart'), row.get('relatedDepart'))))
                tag_rows = normalized_items(first_data(row.get('tagList')))
                replace_tag_rows(cur, jcode, [first_text(r.get('tag'), r.get('name'), r.get('value')) for r in tag_rows if first_text(r.get('tag'), r.get('name'), r.get('value'))] or split_csv(base_row.get('tag')))
                replace_rel_org_rows(cur, jcode, normalized_items(first_data(row.get('jobRelOrgList'), row.get('rel_org'), row.get('relOrg'))))
                log(f'job {jcode}: 상세 동기화 완료 ({common.safe_url(url)})')
        conn.commit()
    finally:
        conn.close()


def sync_all(args):
    sync_code_list()
    sync_job_list(keyword=args.keyword, max_pages=args.max_pages)
    sync_subject_list()
    sync_job_detail(limit=args.detail_limit)
    sync_subject_detail(limit=args.subject_detail_limit)


def build_parser():
    parser = argparse.ArgumentParser(description='career 수집기 초안')
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('plan')
    sub.add_parser('init-db')
    sub.add_parser('sync-code-list')
    sub.add_parser('sync-school-list')
    sub.add_parser('sync-subject-list')
    sub.add_parser('sync-aptitude-meta')

    subject_detail_parser = sub.add_parser('sync-subject-detail')
    subject_detail_parser.add_argument('--school', default='')
    subject_detail_parser.add_argument('--seq', type=int, default=0)
    subject_detail_parser.add_argument('--limit', type=int, default=0)

    job_list_parser = sub.add_parser('sync-job-list')
    job_list_parser.add_argument('--keyword', default='')
    job_list_parser.add_argument('--max-pages', type=int, default=0)

    job_detail_parser = sub.add_parser('sync-job-detail')
    job_detail_parser.add_argument('--seq', type=int, default=0)
    job_detail_parser.add_argument('--limit', type=int, default=0)

    sync_all_parser = sub.add_parser('sync-all')
    sync_all_parser.add_argument('--keyword', default='')
    sync_all_parser.add_argument('--max-pages', type=int, default=0)
    sync_all_parser.add_argument('--detail-limit', type=int, default=0)
    sync_all_parser.add_argument('--subject-detail-limit', type=int, default=0)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == 'plan':
        print_plan()
        return
    if args.command == 'init-db':
        ensure_tables()
        log('DB 초기화 완료')
        return
    if args.command == 'sync-code-list':
        sync_code_list()
        return
    if args.command == 'sync-school-list':
        sync_school_list()
        return
    if args.command == 'sync-subject-list':
        sync_subject_list()
        return
    if args.command == 'sync-aptitude-meta':
        sync_aptitude_meta()
        return
    if args.command == 'sync-subject-detail':
        sync_subject_detail(school=args.school, seq=args.seq, limit=args.limit)
        return
    if args.command == 'sync-job-list':
        sync_job_list(keyword=args.keyword, max_pages=args.max_pages)
        return
    if args.command == 'sync-job-detail':
        with append_job_detail_log():
            sync_job_detail(seq=args.seq, limit=args.limit)
        return
    if args.command == 'sync-all':
        sync_all(args)
        return
    parser.error('알 수 없는 명령입니다.')


if __name__ == '__main__':
    main()
