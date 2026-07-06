#!/usr/bin/env python3
import argparse
import hashlib
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError

from include import common
from include.common import connect_db, fetch_xml, first_non_empty, int_or_zero, log, parse_xml_response, save_raw, text, value_or_default


BASE_DIR = Path(__file__).resolve().parent
API_SPEC_PATH = BASE_DIR / 'API_SPEC.md'

SCHOOL_INDICATOR_REQUEST_DELAY = 0.6
SCHOOL_INDICATOR_DELAY_BY_ENDPOINT = {
    '/getComparisonFullTimeFacultyResearchCrntSt': 3.0,
    '/getNoticeFullTimeFacultyResearchCrntSt': 2.0,
}
SCHOOL_INDICATOR_429_COOLDOWN = 180
SCHOOL_INDICATOR_SKIP_LOG_NAME = 'sync_school_indicator_skips.tsv'


CODE_TYPE_MAP = {
    '/getCodeByRegion': 'region',
    '/getCodeByFound': 'found',
    '/getCodeByType': 'school_type',
    '/getCodeByKind': 'school_kind',
    '/getKeyIndicatorCode': 'key_indicator',
    '/getCodeByLargeSeries': 'large_series',
    '/getCodeByMiddleSeries': 'middle_series',
    '/getCodeBySmallSeries': 'small_series',
    '/getCodeBySeriesSystem': 'series_system',
    '/getCodeByPrincipalSchoolBranchSchool': 'principal_branch',
    '/getCodeByLessonTerm': 'lesson_term',
    '/getCodeByDegreeCourse': 'degree_course',
    '/getCodeByDayAndNight': 'day_night',
    '/getCodeByCollege': 'college',
    '/getCodeByMajorStatus': 'major_status',
    '/getCodeByMajorCharacter': 'major_character',
    '/getCodeByOneselfSeries': 'oneself_series',
}


CREATE_STATEMENTS = [
    f"""
    CREATE DATABASE IF NOT EXISTS {common.DB_NAME}
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.code_list (
        code_type varchar(30) NOT NULL,
        code varchar(30) NOT NULL,
        name varchar(100) NOT NULL,
        parent_code varchar(30) NOT NULL default '',
        rmk varchar(300) NOT NULL default '',
        recv_time datetime NOT NULL,
        PRIMARY KEY (code_type, code),
        KEY name_idx (name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.year_list (
        year_type varchar(30) NOT NULL,
        year_val char(4) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (year_type, year_val)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.school_list (
        schl_id varchar(20) NOT NULL,
        svy_yr char(4) NOT NULL,
        name varchar(100) NOT NULL,
        full_name varchar(150) NOT NULL default '',
        name_eng varchar(150) NOT NULL default '',
        div_cd varchar(20) NOT NULL default '',
        div_name varchar(50) NOT NULL default '',
        kind_cd varchar(20) NOT NULL default '',
        kind_name varchar(50) NOT NULL default '',
        est_cd varchar(20) NOT NULL default '',
        est_name varchar(50) NOT NULL default '',
        campus_cd varchar(20) NOT NULL default '',
        campus_name varchar(50) NOT NULL default '',
        region_cd varchar(20) NOT NULL default '',
        region_name varchar(50) NOT NULL default '',
        area_cd varchar(20) NOT NULL default '',
        area_name varchar(50) NOT NULL default '',
        post_no varchar(20) NOT NULL default '',
        address varchar(200) NOT NULL default '',
        phone varchar(30) NOT NULL default '',
        fax varchar(30) NOT NULL default '',
        url varchar(200) NOT NULL default '',
        estb_date char(8) NOT NULL default '',
        lst_updt_dtm varchar(30) NOT NULL default '',
        recv_time datetime NOT NULL,
        PRIMARY KEY (schl_id, svy_yr),
        KEY name_idx (name),
        KEY region_cd_idx (region_cd),
        KEY div_cd_idx (div_cd),
        KEY kind_cd_idx (kind_cd),
        KEY est_cd_idx (est_cd)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.subject_list (
        schl_id varchar(20) NOT NULL,
        svy_yr char(4) NOT NULL,
        schl_mjr_id varchar(30) NOT NULL,
        major_id varchar(30) NOT NULL,
        std_major_id varchar(30) NOT NULL default '',
        name varchar(150) NOT NULL,
        college_name varchar(100) NOT NULL default '',
        srs_lclft_cd varchar(20) NOT NULL default '',
        srs_lclft_name varchar(100) NOT NULL default '',
        srs_mclft_cd varchar(20) NOT NULL default '',
        srs_mclft_name varchar(100) NOT NULL default '',
        srs_sclft_cd varchar(20) NOT NULL default '',
        srs_sclft_name varchar(100) NOT NULL default '',
        area_cd varchar(20) NOT NULL default '',
        area_name varchar(50) NOT NULL default '',
        area_signgu_cd varchar(20) NOT NULL default '',
        area_signgu_name varchar(50) NOT NULL default '',
        degree_name varchar(50) NOT NULL default '',
        lesson_term_name varchar(50) NOT NULL default '',
        oneself_series_name varchar(50) NOT NULL default '',
        major_char_name varchar(50) NOT NULL default '',
        major_stat_name varchar(50) NOT NULL default '',
        school_kind_name varchar(50) NOT NULL default '',
        entrance_quota int unsigned NOT NULL default 0,
        graduate_num int unsigned NOT NULL default 0,
        day_night_name varchar(30) NOT NULL default '',
        edu_course_text text NOT NULL,
        employ_path_text text NOT NULL,
        major_updt_dtm varchar(30) NOT NULL default '',
        lst_updt_dtm varchar(30) NOT NULL default '',
        recv_time datetime NOT NULL,
        PRIMARY KEY (schl_id, svy_yr, schl_mjr_id),
        KEY major_id_idx (major_id),
        KEY name_idx (name),
        KEY area_cd_idx (area_cd),
        KEY schl_id_idx (schl_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.school_indicator_list (
        api_id varchar(80) NOT NULL,
        indct_id varchar(30) NOT NULL,
        schl_id varchar(20) NOT NULL,
        svy_yr char(4) NOT NULL,
        indct_yr char(4) NOT NULL default '',
        apy_yr char(4) NOT NULL default '',
        schl_name varchar(100) NOT NULL default '',
        schl_div_name varchar(50) NOT NULL default '',
        schl_estb_name varchar(50) NOT NULL default '',
        val1 varchar(100) NOT NULL default '',
        val2 varchar(100) NOT NULL default '',
        val3 varchar(100) NOT NULL default '',
        val4 varchar(100) NOT NULL default '',
        val5 varchar(100) NOT NULL default '',
        val6 varchar(100) NOT NULL default '',
        val7 varchar(100) NOT NULL default '',
        val8 varchar(100) NOT NULL default '',
        val9 varchar(100) NOT NULL default '',
        val10 varchar(100) NOT NULL default '',
        avg_val varchar(100) NOT NULL default '',
        img_url varchar(200) NOT NULL default '',
        recv_time datetime NOT NULL,
        PRIMARY KEY (api_id, indct_id, schl_id, svy_yr),
        KEY schl_id_idx (schl_id),
        KEY indct_id_idx (indct_id),
        KEY api_schl_idx (api_id, schl_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.regional_indicator_list (
        api_id varchar(80) NOT NULL,
        indct_id varchar(30) NOT NULL,
        schl_div_cd varchar(20) NOT NULL,
        region_name varchar(50) NOT NULL default '',
        region_rmk varchar(200) NOT NULL default '',
        field_type1 varchar(50) NOT NULL default '',
        field_type2 varchar(50) NOT NULL default '',
        field_type3 varchar(50) NOT NULL default '',
        field_type4 varchar(50) NOT NULL default '',
        field_type5 varchar(50) NOT NULL default '',
        field_type6 varchar(50) NOT NULL default '',
        field_type7 varchar(50) NOT NULL default '',
        field_val1 varchar(100) NOT NULL default '',
        field_val2 varchar(100) NOT NULL default '',
        field_val3 varchar(100) NOT NULL default '',
        field_val4 varchar(100) NOT NULL default '',
        field_val5 varchar(100) NOT NULL default '',
        field_val6 varchar(100) NOT NULL default '',
        field_val7 varchar(100) NOT NULL default '',
        first_svy_yr char(4) NOT NULL default '',
        second_svy_yr char(4) NOT NULL default '',
        third_svy_yr char(4) NOT NULL default '',
        first_val varchar(100) NOT NULL default '',
        second_val varchar(100) NOT NULL default '',
        third_val varchar(100) NOT NULL default '',
        first_schl_cnt varchar(30) NOT NULL default '',
        second_schl_cnt varchar(30) NOT NULL default '',
        third_schl_cnt varchar(30) NOT NULL default '',
        recv_time datetime NOT NULL,
        PRIMARY KEY (api_id, indct_id, schl_div_cd, region_name, region_rmk),
        KEY schl_div_cd_idx (schl_div_cd),
        KEY indct_id_idx (indct_id),
        KEY api_indct_idx (api_id, indct_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {common.DB_NAME}.startup_support_list (
        api_id varchar(80) NOT NULL,
        schl_id varchar(20) NOT NULL,
        svy_yr char(4) NOT NULL,
        indct_id varchar(30) NOT NULL,
        indct_yr char(4) NOT NULL default '',
        seq int unsigned NOT NULL,
        item_key varchar(50) NOT NULL,
        item_value varchar(300) NOT NULL,
        recv_time datetime NOT NULL,
        PRIMARY KEY (api_id, schl_id, svy_yr, indct_id, seq, item_key),
        KEY indct_id_idx (indct_id),
        KEY item_key_idx (item_key)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
]


def parse_api_spec():
    lines = API_SPEC_PATH.read_text().splitlines()
    endpoints = []
    current_service = ''
    current_host = ''
    current = None
    in_params = False

    for line in lines:
        if line.startswith('## '):
            if current is not None:
                endpoints.append(current)
                current = None
            current_service = line[3:].strip()
            current_host = ''
            in_params = False
            continue

        if line.startswith('- host: `'):
            current_host = line.split('`')[1]
            continue

        if line.startswith('### `/get'):
            if current is not None:
                endpoints.append(current)
            current = {
                'service': current_service,
                'host': current_host,
                'path': line.split('`')[1],
                'required_params': [],
                'optional_params': [],
            }
            in_params = False
            continue

        if current is None:
            continue

        if line.startswith('- query parameters:'):
            in_params = True
            continue

        if in_params and line.startswith(' - `'):
            match = re.match(r" - `([^`]+)` \((required|optional),", line)
            if not match:
                continue
            param_name, required_flag = match.groups()
            if required_flag == 'required':
                current['required_params'].append(param_name)
            else:
                current['optional_params'].append(param_name)
            continue

        if in_params and not line.startswith(' - `'):
            in_params = False

    if current is not None:
        endpoints.append(current)

    return endpoints


def endpoint_name(path):
    return path.lstrip('/')


def is_code_endpoint(endpoint):
    return endpoint['path'] in CODE_TYPE_MAP


def is_year_endpoint(endpoint):
    return endpoint['path'] in ('/getNoticeSvyYear', '/getComparisonPubYear')


def is_school_master_endpoint(endpoint):
    return endpoint['path'] in (
        '/getUniversityCode',
        '/getSchoolInfo',
        '/getNoticeUniversitySearchList',
        '/getComparisonUniversitySearchList',
    )


def is_subject_endpoint(endpoint):
    return endpoint['path'] in ('/getUniversityMajorCode', '/getSchoolMajorInfo')


def is_regional_endpoint(endpoint):
    return endpoint['path'].startswith('/getRegional')


def is_startup_endpoint(endpoint):
    return endpoint['host'].endswith('/IndustryAcademicCooperationService')


def is_school_indicator_endpoint(endpoint):
    if is_code_endpoint(endpoint) or is_year_endpoint(endpoint):
        return False
    if is_school_master_endpoint(endpoint) or is_subject_endpoint(endpoint):
        return False
    if is_regional_endpoint(endpoint) or is_startup_endpoint(endpoint):
        return False
    return True


def classify(endpoint):
    if is_code_endpoint(endpoint) or is_year_endpoint(endpoint):
        return 'metadata'
    if is_school_master_endpoint(endpoint):
        return 'school_master'
    if is_subject_endpoint(endpoint):
        return 'subject_master'
    if is_regional_endpoint(endpoint):
        return 'regional'
    if is_startup_endpoint(endpoint):
        return 'startup'
    return 'school_indicator'


def schedule_group(endpoint):
    if endpoint['path'] in (
        '/getCodeByRegion',
        '/getCodeByFound',
        '/getCodeByType',
        '/getCodeByKind',
        '/getKeyIndicatorCode',
        '/getComparisonPubYear',
        '/getNoticeSvyYear',
        '/getCodeByLargeSeries',
        '/getCodeByMiddleSeries',
        '/getCodeBySmallSeries',
        '/getCodeBySeriesSystem',
        '/getCodeByPrincipalSchoolBranchSchool',
        '/getCodeByLessonTerm',
        '/getCodeByDegreeCourse',
        '/getCodeByDayAndNight',
        '/getCodeByCollege',
        '/getCodeByMajorStatus',
        '/getCodeByMajorCharacter',
        '/getCodeByOneselfSeries',
    ):
        return 'monthly_metadata'
    if is_school_master_endpoint(endpoint) or is_subject_endpoint(endpoint):
        return 'weekly_master'
    if is_regional_endpoint(endpoint) or is_startup_endpoint(endpoint) or is_school_indicator_endpoint(endpoint):
        return 'monthly_statistics'
    return 'manual_review'


def fetch_pages(endpoint, params, job_name):
    all_items = []
    page_no = 1
    total_count = None

    while True:
        page_params = dict(params)
        page_params['pageNo'] = page_no
        page_params['numOfRows'] = 1000
        url, xml_bytes = fetch_xml(endpoint['host'], endpoint['path'], page_params)
        save_raw(job_name, endpoint_name(endpoint['path']), page_no, xml_bytes)
        parsed = parse_xml_response(xml_bytes)

        if parsed['result_code'] not in ('', '00'):
            log(f'경고: {endpoint["path"]} resultCode={parsed["result_code"]} resultMsg={parsed["result_msg"]} url={url}')

        if total_count is None:
            total_count = parsed['total_count']

        items = parsed['items']
        all_items.extend(items)

        if not items:
            break
        if parsed['num_of_rows'] == 0:
            break
        if len(all_items) >= total_count > 0:
            break
        if len(items) < page_params['numOfRows']:
            break

        page_no += 1

    return all_items


def ensure_schema():
    con = connect_db(autocommit=True)
    try:
        with con.cursor() as cur:
            for stmt in CREATE_STATEMENTS:
                cur.execute(stmt)
        log('스키마 확인 완료')
    finally:
        con.close()


def upsert_code_rows(cur, code_type, items):
    rows = []
    for item in items:
        code = value_or_default(item, 'cdid')
        name = value_or_default(item, 'cdnm')
        if code == '':
            continue
        rows.append((
            code_type,
            code,
            name,
            '',
            value_or_default(item, 'rmk'),
        ))

    if not rows:
        return 0

    cur.executemany(
        f"""
        INSERT INTO {common.DB_NAME}.code_list
        (code_type, code, name, parent_code, rmk, recv_time)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            name=VALUES(name),
            parent_code=VALUES(parent_code),
            rmk=VALUES(rmk),
            recv_time=VALUES(recv_time)
        """,
        rows,
    )
    return len(rows)


def upsert_year_rows(cur, year_type, items):
    rows = []
    for item in items:
        year_val = value_or_default(item, 'yearVal')
        if year_val == '':
            continue
        rows.append((year_type, year_val))

    if not rows:
        return 0

    cur.executemany(
        f"""
        INSERT INTO {common.DB_NAME}.year_list
        (year_type, year_val, recv_time)
        VALUES (%s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            recv_time=VALUES(recv_time)
        """,
        rows,
    )
    return len(rows)


def upsert_school_row(cur, row):
    cur.execute(
        f"""
        INSERT INTO {common.DB_NAME}.school_list (
            schl_id, svy_yr, name, full_name, name_eng,
            div_cd, div_name, kind_cd, kind_name, est_cd, est_name,
            campus_cd, campus_name, region_cd, region_name,
            area_cd, area_name, post_no, address, phone, fax, url,
            estb_date, lst_updt_dtm, recv_time
        ) VALUES (
            %(schl_id)s, %(svy_yr)s, %(name)s, %(full_name)s, %(name_eng)s,
            %(div_cd)s, %(div_name)s, %(kind_cd)s, %(kind_name)s, %(est_cd)s, %(est_name)s,
            %(campus_cd)s, %(campus_name)s, %(region_cd)s, %(region_name)s,
            %(area_cd)s, %(area_name)s, %(post_no)s, %(address)s, %(phone)s, %(fax)s, %(url)s,
            %(estb_date)s, %(lst_updt_dtm)s, NOW()
        )
        ON DUPLICATE KEY UPDATE
            name=IF(VALUES(name) <> '', VALUES(name), name),
            full_name=IF(VALUES(full_name) <> '', VALUES(full_name), full_name),
            name_eng=IF(VALUES(name_eng) <> '', VALUES(name_eng), name_eng),
            div_cd=IF(VALUES(div_cd) <> '', VALUES(div_cd), div_cd),
            div_name=IF(VALUES(div_name) <> '', VALUES(div_name), div_name),
            kind_cd=IF(VALUES(kind_cd) <> '', VALUES(kind_cd), kind_cd),
            kind_name=IF(VALUES(kind_name) <> '', VALUES(kind_name), kind_name),
            est_cd=IF(VALUES(est_cd) <> '', VALUES(est_cd), est_cd),
            est_name=IF(VALUES(est_name) <> '', VALUES(est_name), est_name),
            campus_cd=IF(VALUES(campus_cd) <> '', VALUES(campus_cd), campus_cd),
            campus_name=IF(VALUES(campus_name) <> '', VALUES(campus_name), campus_name),
            region_cd=IF(VALUES(region_cd) <> '', VALUES(region_cd), region_cd),
            region_name=IF(VALUES(region_name) <> '', VALUES(region_name), region_name),
            area_cd=IF(VALUES(area_cd) <> '', VALUES(area_cd), area_cd),
            area_name=IF(VALUES(area_name) <> '', VALUES(area_name), area_name),
            post_no=IF(VALUES(post_no) <> '', VALUES(post_no), post_no),
            address=IF(VALUES(address) <> '', VALUES(address), address),
            phone=IF(VALUES(phone) <> '', VALUES(phone), phone),
            fax=IF(VALUES(fax) <> '', VALUES(fax), fax),
            url=IF(VALUES(url) <> '', VALUES(url), url),
            estb_date=IF(VALUES(estb_date) <> '', VALUES(estb_date), estb_date),
            lst_updt_dtm=IF(VALUES(lst_updt_dtm) <> '', VALUES(lst_updt_dtm), lst_updt_dtm),
            recv_time=VALUES(recv_time)
        """,
        row,
    )


def subject_seed_from_major_code(cur, item):
    row = {
        'schl_id': value_or_default(item, 'schlId'),
        'svy_yr': value_or_default(item, 'svyYr'),
        'schl_mjr_id': value_or_default(item, 'schlMjrId'),
        'major_id': first_non_empty(value_or_default(item, 'kediMjrId'), value_or_default(item, 'mjrId')),
        'std_major_id': value_or_default(item, 'stdClftMjrId'),
        'name': first_non_empty(value_or_default(item, 'korMjrNm'), value_or_default(item, 'mjrNm')),
        'college_name': value_or_default(item, 'clgNm'),
        'srs_lclft_cd': value_or_default(item, 'srsLclftCd'),
        'srs_lclft_name': value_or_default(item, 'korSrsLclftNm'),
        'srs_mclft_cd': value_or_default(item, 'srsMclftCd'),
        'srs_mclft_name': value_or_default(item, 'korSrsMclftNm'),
        'srs_sclft_cd': value_or_default(item, 'srsSclftCd'),
        'srs_sclft_name': value_or_default(item, 'korSrsSclftNm'),
        'area_cd': value_or_default(item, 'mjrAreaCd'),
        'area_name': value_or_default(item, 'mjrAreaNm'),
        'area_signgu_cd': value_or_default(item, 'mjrAreaSignguCd'),
        'area_signgu_name': value_or_default(item, 'mjrAreaSignguNm'),
        'degree_name': first_non_empty(value_or_default(item, 'pbnfDgriCrseDivNm'), value_or_default(item, 'degreeNm')),
        'lesson_term_name': value_or_default(item, 'lsnTrmNm'),
        'oneself_series_name': value_or_default(item, 'onsfSrsClftNm'),
        'major_char_name': value_or_default(item, 'schlMjrCharNm'),
        'major_stat_name': value_or_default(item, 'schlMjrStatNm'),
        'school_kind_name': value_or_default(item, 'schlKndNm'),
        'entrance_quota': int_or_zero(item.get('eschlPscpNum')),
        'graduate_num': int_or_zero(item.get('grdtNum')),
        'day_night_name': value_or_default(item, 'dghtDivNm'),
        'edu_course_text': value_or_default(item, 'edcCrseLtrCtnt'),
        'employ_path_text': value_or_default(item, 'pwayEmplLtrCtnt'),
        'major_updt_dtm': value_or_default(item, 'mjrUpdtDtm'),
        'lst_updt_dtm': value_or_default(item, 'lstUpdtDtm'),
    }
    if row['schl_id'] == '' or row['svy_yr'] == '' or row['schl_mjr_id'] == '':
        return

    cur.execute(
        f"""
        INSERT INTO {common.DB_NAME}.subject_list (
            schl_id, svy_yr, schl_mjr_id, major_id, std_major_id, name,
            college_name, srs_lclft_cd, srs_lclft_name, srs_mclft_cd, srs_mclft_name,
            srs_sclft_cd, srs_sclft_name, area_cd, area_name, area_signgu_cd, area_signgu_name,
            degree_name, lesson_term_name, oneself_series_name, major_char_name, major_stat_name,
            school_kind_name, entrance_quota, graduate_num, day_night_name, edu_course_text,
            employ_path_text, major_updt_dtm, lst_updt_dtm, recv_time
        ) VALUES (
            %(schl_id)s, %(svy_yr)s, %(schl_mjr_id)s, %(major_id)s, %(std_major_id)s, %(name)s,
            %(college_name)s, %(srs_lclft_cd)s, %(srs_lclft_name)s, %(srs_mclft_cd)s, %(srs_mclft_name)s,
            %(srs_sclft_cd)s, %(srs_sclft_name)s, %(area_cd)s, %(area_name)s, %(area_signgu_cd)s, %(area_signgu_name)s,
            %(degree_name)s, %(lesson_term_name)s, %(oneself_series_name)s, %(major_char_name)s, %(major_stat_name)s,
            %(school_kind_name)s, %(entrance_quota)s, %(graduate_num)s, %(day_night_name)s, %(edu_course_text)s,
            %(employ_path_text)s, %(major_updt_dtm)s, %(lst_updt_dtm)s, NOW()
        )
        ON DUPLICATE KEY UPDATE
            major_id=IF(VALUES(major_id) <> '', VALUES(major_id), major_id),
            std_major_id=IF(VALUES(std_major_id) <> '', VALUES(std_major_id), std_major_id),
            name=IF(VALUES(name) <> '', VALUES(name), name),
            college_name=IF(VALUES(college_name) <> '', VALUES(college_name), college_name),
            srs_lclft_cd=IF(VALUES(srs_lclft_cd) <> '', VALUES(srs_lclft_cd), srs_lclft_cd),
            srs_lclft_name=IF(VALUES(srs_lclft_name) <> '', VALUES(srs_lclft_name), srs_lclft_name),
            srs_mclft_cd=IF(VALUES(srs_mclft_cd) <> '', VALUES(srs_mclft_cd), srs_mclft_cd),
            srs_mclft_name=IF(VALUES(srs_mclft_name) <> '', VALUES(srs_mclft_name), srs_mclft_name),
            srs_sclft_cd=IF(VALUES(srs_sclft_cd) <> '', VALUES(srs_sclft_cd), srs_sclft_cd),
            srs_sclft_name=IF(VALUES(srs_sclft_name) <> '', VALUES(srs_sclft_name), srs_sclft_name),
            area_cd=IF(VALUES(area_cd) <> '', VALUES(area_cd), area_cd),
            area_name=IF(VALUES(area_name) <> '', VALUES(area_name), area_name),
            area_signgu_cd=IF(VALUES(area_signgu_cd) <> '', VALUES(area_signgu_cd), area_signgu_cd),
            area_signgu_name=IF(VALUES(area_signgu_name) <> '', VALUES(area_signgu_name), area_signgu_name),
            degree_name=IF(VALUES(degree_name) <> '', VALUES(degree_name), degree_name),
            lesson_term_name=IF(VALUES(lesson_term_name) <> '', VALUES(lesson_term_name), lesson_term_name),
            oneself_series_name=IF(VALUES(oneself_series_name) <> '', VALUES(oneself_series_name), oneself_series_name),
            major_char_name=IF(VALUES(major_char_name) <> '', VALUES(major_char_name), major_char_name),
            major_stat_name=IF(VALUES(major_stat_name) <> '', VALUES(major_stat_name), major_stat_name),
            school_kind_name=IF(VALUES(school_kind_name) <> '', VALUES(school_kind_name), school_kind_name),
            entrance_quota=IF(VALUES(entrance_quota) <> 0, VALUES(entrance_quota), entrance_quota),
            graduate_num=IF(VALUES(graduate_num) <> 0, VALUES(graduate_num), graduate_num),
            day_night_name=IF(VALUES(day_night_name) <> '', VALUES(day_night_name), day_night_name),
            edu_course_text=IF(VALUES(edu_course_text) <> '', VALUES(edu_course_text), edu_course_text),
            employ_path_text=IF(VALUES(employ_path_text) <> '', VALUES(employ_path_text), employ_path_text),
            major_updt_dtm=IF(VALUES(major_updt_dtm) <> '', VALUES(major_updt_dtm), major_updt_dtm),
            lst_updt_dtm=IF(VALUES(lst_updt_dtm) <> '', VALUES(lst_updt_dtm), lst_updt_dtm),
            recv_time=VALUES(recv_time)
        """,
        row,
    )


def subject_merge_from_school_major_info(cur, schl_id, item):
    major_id = value_or_default(item, 'kediMjrId')
    name = value_or_default(item, 'korMjrNm')
    svy_yr = value_or_default(item, 'svyYr')
    if schl_id == '' or svy_yr == '' or major_id == '' or name == '':
        return

    update_row = {
        'schl_id': schl_id,
        'svy_yr': svy_yr,
        'major_id': major_id,
        'name': name,
        'std_major_id': value_or_default(item, 'stdClftMjrId'),
        'college_name': value_or_default(item, 'clgNm'),
        'area_cd': value_or_default(item, 'mjrAreaCd'),
        'area_name': value_or_default(item, 'mjrAreaNm'),
        'area_signgu_cd': value_or_default(item, 'mjrAreaSignguCd'),
        'area_signgu_name': value_or_default(item, 'mjrAreaSignguNm'),
        'degree_name': value_or_default(item, 'pbnfDgriCrseDivNm'),
        'lesson_term_name': value_or_default(item, 'lsnTrmNm'),
        'oneself_series_name': value_or_default(item, 'onsfSrsClftNm'),
        'major_char_name': value_or_default(item, 'schlMjrCharNm'),
        'major_stat_name': value_or_default(item, 'schlMjrStatNm'),
        'school_kind_name': value_or_default(item, 'schlKndNm'),
        'entrance_quota': int_or_zero(item.get('eschlPscpNum')),
        'graduate_num': int_or_zero(item.get('grdtNum')),
        'day_night_name': value_or_default(item, 'dghtDivNm'),
        'edu_course_text': value_or_default(item, 'edcCrseLtrCtnt'),
        'employ_path_text': value_or_default(item, 'pwayEmplLtrCtnt'),
        'major_updt_dtm': value_or_default(item, 'mjrUpdtDtm'),
        'lst_updt_dtm': value_or_default(item, 'lstUpdtDtm'),
    }

    updated = cur.execute(
        f"""
        UPDATE {common.DB_NAME}.subject_list
        SET
            std_major_id=IF(%(std_major_id)s <> '', %(std_major_id)s, std_major_id),
            college_name=IF(%(college_name)s <> '', %(college_name)s, college_name),
            area_cd=IF(%(area_cd)s <> '', %(area_cd)s, area_cd),
            area_name=IF(%(area_name)s <> '', %(area_name)s, area_name),
            area_signgu_cd=IF(%(area_signgu_cd)s <> '', %(area_signgu_cd)s, area_signgu_cd),
            area_signgu_name=IF(%(area_signgu_name)s <> '', %(area_signgu_name)s, area_signgu_name),
            degree_name=IF(%(degree_name)s <> '', %(degree_name)s, degree_name),
            lesson_term_name=IF(%(lesson_term_name)s <> '', %(lesson_term_name)s, lesson_term_name),
            oneself_series_name=IF(%(oneself_series_name)s <> '', %(oneself_series_name)s, oneself_series_name),
            major_char_name=IF(%(major_char_name)s <> '', %(major_char_name)s, major_char_name),
            major_stat_name=IF(%(major_stat_name)s <> '', %(major_stat_name)s, major_stat_name),
            school_kind_name=IF(%(school_kind_name)s <> '', %(school_kind_name)s, school_kind_name),
            entrance_quota=IF(%(entrance_quota)s <> 0, %(entrance_quota)s, entrance_quota),
            graduate_num=IF(%(graduate_num)s <> 0, %(graduate_num)s, graduate_num),
            day_night_name=IF(%(day_night_name)s <> '', %(day_night_name)s, day_night_name),
            edu_course_text=IF(%(edu_course_text)s <> '', %(edu_course_text)s, edu_course_text),
            employ_path_text=IF(%(employ_path_text)s <> '', %(employ_path_text)s, employ_path_text),
            major_updt_dtm=IF(%(major_updt_dtm)s <> '', %(major_updt_dtm)s, major_updt_dtm),
            lst_updt_dtm=IF(%(lst_updt_dtm)s <> '', %(lst_updt_dtm)s, lst_updt_dtm),
            recv_time=NOW()
        WHERE schl_id=%(schl_id)s
          AND svy_yr=%(svy_yr)s
          AND major_id=%(major_id)s
          AND name=%(name)s
        """,
        update_row,
    )

    if updated:
        return

    synthetic = hashlib.md5(f'{schl_id}|{svy_yr}|{major_id}|{name}'.encode()).hexdigest()[:30]
    subject_seed_from_major_code(
        cur,
        {
            'schlId': schl_id,
            'svyYr': svy_yr,
            'schlMjrId': synthetic,
            'kediMjrId': major_id,
            'stdClftMjrId': update_row['std_major_id'],
            'korMjrNm': name,
            'clgNm': update_row['college_name'],
            'mjrAreaCd': update_row['area_cd'],
            'mjrAreaNm': update_row['area_name'],
            'mjrAreaSignguCd': update_row['area_signgu_cd'],
            'mjrAreaSignguNm': update_row['area_signgu_name'],
            'pbnfDgriCrseDivNm': update_row['degree_name'],
            'lsnTrmNm': update_row['lesson_term_name'],
            'onsfSrsClftNm': update_row['oneself_series_name'],
            'schlMjrCharNm': update_row['major_char_name'],
            'schlMjrStatNm': update_row['major_stat_name'],
            'schlKndNm': update_row['school_kind_name'],
            'eschlPscpNum': update_row['entrance_quota'],
            'grdtNum': update_row['graduate_num'],
            'dghtDivNm': update_row['day_night_name'],
            'edcCrseLtrCtnt': update_row['edu_course_text'],
            'pwayEmplLtrCtnt': update_row['employ_path_text'],
            'mjrUpdtDtm': update_row['major_updt_dtm'],
            'lstUpdtDtm': update_row['lst_updt_dtm'],
        },
    )


def upsert_school_indicator(cur, api_id, item, params):
    schl_id = first_non_empty(value_or_default(item, 'schlId'), text(params.get('schlId')))
    svy_yr = first_non_empty(value_or_default(item, 'svyYr'), text(params.get('svyYr')))
    indct_id = first_non_empty(value_or_default(item, 'indctId'), text(params.get('indctId')), api_id)
    if schl_id == '' or svy_yr == '':
        return

    cur.execute(
        f"""
        INSERT INTO {common.DB_NAME}.school_indicator_list (
            api_id, indct_id, schl_id, svy_yr, indct_yr, apy_yr,
            schl_name, schl_div_name, schl_estb_name,
            val1, val2, val3, val4, val5, val6, val7, val8, val9, val10,
            avg_val, img_url, recv_time
        ) VALUES (
            %(api_id)s, %(indct_id)s, %(schl_id)s, %(svy_yr)s, %(indct_yr)s, %(apy_yr)s,
            %(schl_name)s, %(schl_div_name)s, %(schl_estb_name)s,
            %(val1)s, %(val2)s, %(val3)s, %(val4)s, %(val5)s, %(val6)s, %(val7)s, %(val8)s, %(val9)s, %(val10)s,
            %(avg_val)s, %(img_url)s, NOW()
        )
        ON DUPLICATE KEY UPDATE
            indct_yr=IF(VALUES(indct_yr) <> '', VALUES(indct_yr), indct_yr),
            apy_yr=IF(VALUES(apy_yr) <> '', VALUES(apy_yr), apy_yr),
            schl_name=IF(VALUES(schl_name) <> '', VALUES(schl_name), schl_name),
            schl_div_name=IF(VALUES(schl_div_name) <> '', VALUES(schl_div_name), schl_div_name),
            schl_estb_name=IF(VALUES(schl_estb_name) <> '', VALUES(schl_estb_name), schl_estb_name),
            val1=IF(VALUES(val1) <> '', VALUES(val1), val1),
            val2=IF(VALUES(val2) <> '', VALUES(val2), val2),
            val3=IF(VALUES(val3) <> '', VALUES(val3), val3),
            val4=IF(VALUES(val4) <> '', VALUES(val4), val4),
            val5=IF(VALUES(val5) <> '', VALUES(val5), val5),
            val6=IF(VALUES(val6) <> '', VALUES(val6), val6),
            val7=IF(VALUES(val7) <> '', VALUES(val7), val7),
            val8=IF(VALUES(val8) <> '', VALUES(val8), val8),
            val9=IF(VALUES(val9) <> '', VALUES(val9), val9),
            val10=IF(VALUES(val10) <> '', VALUES(val10), val10),
            avg_val=IF(VALUES(avg_val) <> '', VALUES(avg_val), avg_val),
            img_url=IF(VALUES(img_url) <> '', VALUES(img_url), img_url),
            recv_time=VALUES(recv_time)
        """,
        {
            'api_id': api_id,
            'indct_id': indct_id,
            'schl_id': schl_id,
            'svy_yr': svy_yr,
            'indct_yr': value_or_default(item, 'indctYr'),
            'apy_yr': value_or_default(item, 'apyYr'),
            'schl_name': value_or_default(item, 'schlKrnNm'),
            'schl_div_name': value_or_default(item, 'schlDivNm'),
            'schl_estb_name': first_non_empty(value_or_default(item, 'schlEstbNm'), value_or_default(item, 'schlEstbDivNm')),
            'val1': value_or_default(item, 'indctVal1'),
            'val2': value_or_default(item, 'indctVal2'),
            'val3': value_or_default(item, 'indctVal3'),
            'val4': value_or_default(item, 'indctVal4'),
            'val5': value_or_default(item, 'indctVal5'),
            'val6': value_or_default(item, 'indctVal6'),
            'val7': value_or_default(item, 'indctVal7'),
            'val8': value_or_default(item, 'indctVal8'),
            'val9': value_or_default(item, 'indctVal9'),
            'val10': value_or_default(item, 'indctVal10'),
            'avg_val': first_non_empty(value_or_default(item, 'indctAvg'), value_or_default(item, 'avgVal')),
            'img_url': first_non_empty(value_or_default(item, 'indctImg'), value_or_default(item, 'imgUrl')),
        },
    )


def upsert_regional_indicator(cur, api_id, item, params):
    indct_id = first_non_empty(value_or_default(item, 'indctId'), text(params.get('indctId')), api_id)
    schl_div_cd = first_non_empty(value_or_default(item, 'schlDivCd'), text(params.get('schlDivCd')))
    if schl_div_cd == '':
        return

    cur.execute(
        f"""
        INSERT INTO {common.DB_NAME}.regional_indicator_list (
            api_id, indct_id, schl_div_cd, region_name, region_rmk,
            field_type1, field_type2, field_type3, field_type4, field_type5, field_type6, field_type7,
            field_val1, field_val2, field_val3, field_val4, field_val5, field_val6, field_val7,
            first_svy_yr, second_svy_yr, third_svy_yr,
            first_val, second_val, third_val,
            first_schl_cnt, second_schl_cnt, third_schl_cnt,
            recv_time
        ) VALUES (
            %(api_id)s, %(indct_id)s, %(schl_div_cd)s, %(region_name)s, %(region_rmk)s,
            %(field_type1)s, %(field_type2)s, %(field_type3)s, %(field_type4)s, %(field_type5)s, %(field_type6)s, %(field_type7)s,
            %(field_val1)s, %(field_val2)s, %(field_val3)s, %(field_val4)s, %(field_val5)s, %(field_val6)s, %(field_val7)s,
            %(first_svy_yr)s, %(second_svy_yr)s, %(third_svy_yr)s,
            %(first_val)s, %(second_val)s, %(third_val)s,
            %(first_schl_cnt)s, %(second_schl_cnt)s, %(third_schl_cnt)s,
            NOW()
        )
        ON DUPLICATE KEY UPDATE
            field_type1=VALUES(field_type1),
            field_type2=VALUES(field_type2),
            field_type3=VALUES(field_type3),
            field_type4=VALUES(field_type4),
            field_type5=VALUES(field_type5),
            field_type6=VALUES(field_type6),
            field_type7=VALUES(field_type7),
            field_val1=VALUES(field_val1),
            field_val2=VALUES(field_val2),
            field_val3=VALUES(field_val3),
            field_val4=VALUES(field_val4),
            field_val5=VALUES(field_val5),
            field_val6=VALUES(field_val6),
            field_val7=VALUES(field_val7),
            first_svy_yr=VALUES(first_svy_yr),
            second_svy_yr=VALUES(second_svy_yr),
            third_svy_yr=VALUES(third_svy_yr),
            first_val=VALUES(first_val),
            second_val=VALUES(second_val),
            third_val=VALUES(third_val),
            first_schl_cnt=VALUES(first_schl_cnt),
            second_schl_cnt=VALUES(second_schl_cnt),
            third_schl_cnt=VALUES(third_schl_cnt),
            recv_time=VALUES(recv_time)
        """,
        {
            'api_id': api_id,
            'indct_id': indct_id,
            'schl_div_cd': schl_div_cd,
            'region_name': value_or_default(item, 'znNm'),
            'region_rmk': value_or_default(item, 'znNmRmk'),
            'field_type1': value_or_default(item, 'fieldType1'),
            'field_type2': value_or_default(item, 'fieldType2'),
            'field_type3': value_or_default(item, 'fieldType3'),
            'field_type4': value_or_default(item, 'fieldType4'),
            'field_type5': value_or_default(item, 'fieldType5'),
            'field_type6': value_or_default(item, 'fieldType6'),
            'field_type7': value_or_default(item, 'fieldType7'),
            'field_val1': value_or_default(item, 'fieldVal1'),
            'field_val2': value_or_default(item, 'fieldVal2'),
            'field_val3': value_or_default(item, 'fieldVal3'),
            'field_val4': value_or_default(item, 'fieldVal4'),
            'field_val5': value_or_default(item, 'fieldVal5'),
            'field_val6': value_or_default(item, 'fieldVal6'),
            'field_val7': value_or_default(item, 'fieldVal7'),
            'first_svy_yr': value_or_default(item, 'indctFirstSvyYr'),
            'second_svy_yr': value_or_default(item, 'indctSecondSvyYr'),
            'third_svy_yr': value_or_default(item, 'indctThirdSvyYr'),
            'first_val': value_or_default(item, 'indctFirstVal'),
            'second_val': value_or_default(item, 'indctSecondVal'),
            'third_val': value_or_default(item, 'indctThirdVal'),
            'first_schl_cnt': value_or_default(item, 'indctFirstSchlCnt'),
            'second_schl_cnt': value_or_default(item, 'indctSecondSchlCnt'),
            'third_schl_cnt': value_or_default(item, 'indctThirdSchlCnt'),
        },
    )


def insert_startup_support(cur, api_id, item, params, seq_no):
    schl_id = first_non_empty(value_or_default(item, 'schlId'), text(params.get('schlId')))
    svy_yr = first_non_empty(value_or_default(item, 'svyYr'), text(params.get('svyYr')))
    indct_id = first_non_empty(value_or_default(item, 'indctId'), api_id)
    if schl_id == '' or svy_yr == '':
        return

    for key, value in item.items():
        cur.execute(
            f"""
            INSERT INTO {common.DB_NAME}.startup_support_list
            (api_id, schl_id, svy_yr, indct_id, indct_yr, seq, item_key, item_value, recv_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                item_value=VALUES(item_value),
                recv_time=VALUES(recv_time)
            """,
            (
                api_id,
                schl_id,
                svy_yr,
                indct_id,
                value_or_default(item, 'indctYr'),
                seq_no,
                key,
                text(value)[:300],
            ),
        )


def load_years(cur, scope='latest'):
    cur.execute(
        f"""
        SELECT year_type, year_val
        FROM {common.DB_NAME}.year_list
        ORDER BY year_val DESC
        """
    )
    rows = cur.fetchall()
    if not rows:
        return []

    grouped = {}
    for row in rows:
        grouped.setdefault(row['year_type'], []).append(row['year_val'])

    values = []
    for year_type in ('comparison_pub', 'notice_svy'):
        values.extend(grouped.get(year_type, []))

    values = sorted(set(values), reverse=True)
    if scope == 'latest' and values:
        return [values[0]]
    return values


def resolve_school_master_years(cur, endpoint, scope):
    years = load_years(cur, scope='all' if scope == 'latest' else scope)
    if scope != 'latest':
        return years

    for svy_yr in years:
        items = fetch_pages(endpoint, {'serviceKey': common.SERVICE_KEY, 'svyYr': svy_yr}, 'sync_school_master')
        if items:
            return [svy_yr], {svy_yr: items}
    return years[:1], {}


def load_schools(cur, scope='latest'):
    if scope == 'latest':
        cur.execute(
            f"""
            SELECT s1.schl_id, s1.svy_yr, s1.name, s1.div_cd
            FROM {common.DB_NAME}.school_list s1
            JOIN (
                SELECT schl_id, MAX(svy_yr) AS max_svy_yr
                FROM {common.DB_NAME}.school_list
                GROUP BY schl_id
            ) t
              ON t.schl_id = s1.schl_id
             AND t.max_svy_yr = s1.svy_yr
            ORDER BY s1.schl_id
            """
        )
    else:
        cur.execute(
            f"""
            SELECT schl_id, svy_yr, name, div_cd
            FROM {common.DB_NAME}.school_list
            ORDER BY svy_yr DESC, schl_id
            """
        )
    return cur.fetchall()


def slice_schools(schools, school_offset=0, school_limit=None):
    if school_offset < 0:
        raise ValueError('school_offset는 0 이상이어야 합니다')
    if school_limit is not None and school_limit < 1:
        raise ValueError('school_limit는 1 이상이어야 합니다')

    schools = schools[school_offset:]
    if school_limit is not None:
        schools = schools[:school_limit]
    return schools


def filter_schools(schools, school_id='', svy_yr=''):
    filtered = schools
    if school_id:
        filtered = [school for school in filtered if str(school['schl_id']) == str(school_id)]
    if svy_yr:
        filtered = [school for school in filtered if str(school['svy_yr']) == str(svy_yr)]
    return filtered


def filter_endpoints(endpoints, endpoint_path=''):
    if not endpoint_path:
        return endpoints
    filtered = [endpoint for endpoint in endpoints if endpoint['path'] == endpoint_path]
    if not filtered:
        raise RuntimeError(f'조건에 맞는 endpoint가 없습니다: {endpoint_path}')
    return filtered


def filter_indicator_codes(indicator_codes, indicator_code=''):
    if not indicator_code:
        return indicator_codes
    filtered = [code for code in indicator_codes if str(code) == str(indicator_code)]
    if not filtered:
        raise RuntimeError(f'조건에 맞는 지표코드가 없습니다: {indicator_code}')
    return filtered


def filter_skip_rows(rows, endpoint_path='', school_id='', svy_yr='', indicator_code=''):
    filtered = rows
    if endpoint_path:
        filtered = [row for row in filtered if row['endpoint_path'] == endpoint_path]
    if school_id:
        filtered = [row for row in filtered if str(row['school_id']) == str(school_id)]
    if svy_yr:
        filtered = [row for row in filtered if str(row['svy_yr']) == str(svy_yr)]
    if indicator_code:
        filtered = [row for row in filtered if str(row['indicator_code']) == str(indicator_code)]
    return filtered


def school_batch_context(school_offset=0, school_limit=None, school_count=None):
    limit_text = 'all' if school_limit is None else str(school_limit)
    count_text = '?' if school_count is None else str(school_count)
    return f'offset={school_offset} limit={limit_text} count={count_text}'


def load_indicator_codes(cur):
    cur.execute(
        f"""
        SELECT code
        FROM {common.DB_NAME}.code_list
        WHERE code_type='key_indicator'
        ORDER BY code
        """
    )
    return [row['code'] for row in cur.fetchall()]


def load_school_div_codes(cur):
    cur.execute(
        f"""
        SELECT DISTINCT div_cd AS code
        FROM {common.DB_NAME}.school_list
        WHERE div_cd <> ''
        ORDER BY div_cd
        """
    )
    rows = [row['code'] for row in cur.fetchall()]
    if rows:
        return rows

    cur.execute(
        f"""
        SELECT code
        FROM {common.DB_NAME}.code_list
        WHERE code_type IN ('school_type', 'school_kind')
        ORDER BY code
        """
    )
    return [row['code'] for row in cur.fetchall()]


def commit_cursor(cur):
    conn = getattr(cur, 'connection', None)
    if conn is None:
        conn = getattr(cur, '_connection', None)
    if conn is not None:
        conn.commit()


def school_indicator_request_delay(endpoint_path):
    return SCHOOL_INDICATOR_DELAY_BY_ENDPOINT.get(endpoint_path, SCHOOL_INDICATOR_REQUEST_DELAY)


def record_school_indicator_skip(endpoint_path, school_id, svy_yr, indicator_code, reason):
    common.ensure_config_loaded()
    common.ensure_dir(common.LOG_DIR)
    target = Path(common.LOG_DIR) / SCHOOL_INDICATOR_SKIP_LOG_NAME
    with target.open('a', encoding='utf-8') as fp:
        fp.write(
            '\t'.join([
                common.now_text(),
                endpoint_path,
                str(school_id),
                str(svy_yr),
                str(indicator_code),
                reason,
            ]) + '\n'
        )


def load_school_indicator_skip_rows(skip_tsv_path):
    target = Path(skip_tsv_path)
    if not target.exists():
        raise FileNotFoundError(f'skip TSV 파일이 없습니다: {target}')

    rows = []
    for line_no, line in enumerate(target.read_text(encoding='utf-8').splitlines(), start=1):
        if line.strip() == '':
            continue
        cols = line.split('\t')
        if len(cols) < 6:
            log(f'skip TSV {line_no}행 형식 오류 - 건너뜀')
            continue
        rows.append({
            'line_no': line_no,
            'logged_at': cols[0],
            'endpoint_path': cols[1],
            'school_id': cols[2],
            'svy_yr': cols[3],
            'indicator_code': cols[4],
            'reason': '\t'.join(cols[5:]),
        })
    return rows


def dedupe_school_indicator_skip_rows(rows):
    seen = set()
    deduped = []
    for row in rows:
        key = (
            row['endpoint_path'],
            row['school_id'],
            row['svy_yr'],
            row['indicator_code'],
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def default_school_indicator_skip_tsv():
    common.ensure_config_loaded()
    return Path(common.LOG_DIR) / SCHOOL_INDICATOR_SKIP_LOG_NAME


def sync_metadata(cur, endpoints, scope):
    year_endpoints = [e for e in endpoints if is_year_endpoint(e)]
    for endpoint in year_endpoints:
        items = fetch_pages(endpoint, {'serviceKey': common.SERVICE_KEY}, 'sync_code_year')
        year_type = 'notice_svy' if endpoint['path'] == '/getNoticeSvyYear' else 'comparison_pub'
        count = upsert_year_rows(cur, year_type, items)
        log(f'{endpoint["path"]} 년도 {count}건 반영')

    years = load_years(cur, scope=scope)
    for endpoint in endpoints:
        if is_year_endpoint(endpoint):
            continue
        if is_code_endpoint(endpoint):
            if 'svyYr' in endpoint['required_params']:
                for svy_yr in years:
                    params = {'serviceKey': common.SERVICE_KEY, 'svyYr': svy_yr}
                    items = fetch_pages(endpoint, params, 'sync_code_year')
                    if endpoint['path'] == '/getCodeBySeriesSystem':
                        log(f'{endpoint["path"]} 조사년도 {svy_yr} raw만 저장')
                        continue
                    count = upsert_code_rows(cur, CODE_TYPE_MAP[endpoint['path']], items)
                    log(f'{endpoint["path"]} {svy_yr} 코드 {count}건 반영')
            else:
                items = fetch_pages(endpoint, {'serviceKey': common.SERVICE_KEY}, 'sync_code_year')
                count = upsert_code_rows(cur, CODE_TYPE_MAP[endpoint['path']], items)
                log(f'{endpoint["path"]} 코드 {count}건 반영')


def sync_school_master(cur, endpoints, scope):
    university_endpoint = next((e for e in endpoints if e['path'] == '/getUniversityCode'), None)
    if university_endpoint is None:
        raise RuntimeError('getUniversityCode 엔드포인트를 찾을 수 없습니다')

    resolved = resolve_school_master_years(cur, university_endpoint, scope)
    if scope == 'latest':
        years, prefetched_items = resolved
        if years:
            log(f'sync-school-master latest fallback 선택 연도: {years[0]}')
    else:
        years = resolved
        prefetched_items = {}

    if not years:
        raise RuntimeError('year_list가 비어 있습니다. 먼저 sync-code-year 실행 필요')

    for endpoint in endpoints:
        if endpoint['path'] == '/getUniversityCode':
            for svy_yr in years:
                items = prefetched_items.get(svy_yr)
                if items is None:
                    items = fetch_pages(endpoint, {'serviceKey': common.SERVICE_KEY, 'svyYr': svy_yr}, 'sync_school_master')
                for item in items:
                    upsert_school_row(cur, {
                        'schl_id': value_or_default(item, 'schlId'),
                        'svy_yr': value_or_default(item, 'svyYr'),
                        'name': value_or_default(item, 'schlKrnNm'),
                        'full_name': value_or_default(item, 'schlFullNm'),
                        'name_eng': '',
                        'div_cd': value_or_default(item, 'schlDivCd'),
                        'div_name': value_or_default(item, 'schlDivNm'),
                        'kind_cd': value_or_default(item, 'schlKndCd'),
                        'kind_name': value_or_default(item, 'schlKndNm'),
                        'est_cd': value_or_default(item, 'estbDivCd'),
                        'est_name': value_or_default(item, 'estbDivNm'),
                        'campus_cd': value_or_default(item, 'clgcpDivCd'),
                        'campus_name': value_or_default(item, 'clgcpDivNm'),
                        'region_cd': value_or_default(item, 'znCd'),
                        'region_name': value_or_default(item, 'znNm'),
                        'area_cd': '',
                        'area_name': '',
                        'post_no': '',
                        'address': '',
                        'phone': '',
                        'fax': '',
                        'url': '',
                        'estb_date': '',
                        'lst_updt_dtm': '',
                    })
                log(f'{endpoint["path"]} {svy_yr} 학교 {len(items)}건 반영')
                commit_cursor(cur)

    schools = load_schools(cur, scope=scope)
    for endpoint in endpoints:
        if endpoint['path'] == '/getUniversityCode':
            continue
        if endpoint['path'] in ('/getNoticeUniversitySearchList', '/getComparisonUniversitySearchList'):
            for svy_yr in years:
                items = fetch_pages(endpoint, {'serviceKey': common.SERVICE_KEY, 'svyYr': svy_yr}, 'sync_school_master')
                for item in items:
                    upsert_school_row(cur, {
                        'schl_id': value_or_default(item, 'schlId'),
                        'svy_yr': value_or_default(item, 'svyYr'),
                        'name': value_or_default(item, 'schlKrnNm'),
                        'full_name': value_or_default(item, 'schlFullNm'),
                        'name_eng': '',
                        'div_cd': value_or_default(item, 'schlDivCd'),
                        'div_name': value_or_default(item, 'schlDivNm'),
                        'kind_cd': value_or_default(item, 'schlKndCd'),
                        'kind_name': value_or_default(item, 'schlKndNm'),
                        'est_cd': value_or_default(item, 'estbDivCd'),
                        'est_name': value_or_default(item, 'estbDivNm'),
                        'campus_cd': value_or_default(item, 'clgcpDivCd'),
                        'campus_name': value_or_default(item, 'clgcpDivNm'),
                        'region_cd': value_or_default(item, 'znCd'),
                        'region_name': value_or_default(item, 'znNm'),
                        'area_cd': '',
                        'area_name': '',
                        'post_no': '',
                        'address': '',
                        'phone': '',
                        'fax': '',
                        'url': '',
                        'estb_date': '',
                        'lst_updt_dtm': '',
                    })
                log(f'{endpoint["path"]} {svy_yr} 학교검색 {len(items)}건 반영')
                commit_cursor(cur)
            continue

        for school in schools:
            params = {
                'serviceKey': common.SERVICE_KEY,
                'svyYr': school['svy_yr'],
                'schlId': school['schl_id'],
                'schlKrnNm': school['name'],
            }
            items = fetch_pages(endpoint, params, 'sync_school_master')
            for item in items:
                upsert_school_row(cur, {
                    'schl_id': value_or_default(item, 'schlId'),
                    'svy_yr': value_or_default(item, 'svyYr'),
                    'name': first_non_empty(value_or_default(item, 'schlNm'), value_or_default(item, 'schlKrnNm')),
                    'full_name': value_or_default(item, 'schlFullNm'),
                    'name_eng': value_or_default(item, 'schlEngNm'),
                    'div_cd': '',
                    'div_name': value_or_default(item, 'schlDivNm'),
                    'kind_cd': '',
                    'kind_name': value_or_default(item, 'schlKndNm'),
                    'est_cd': '',
                    'est_name': value_or_default(item, 'schlEstbDivNm'),
                    'campus_cd': '',
                    'campus_name': value_or_default(item, 'psbsDivNm'),
                    'region_cd': '',
                    'region_name': '',
                    'area_cd': value_or_default(item, 'pbnfAreaCd'),
                    'area_name': value_or_default(item, 'pbnfAreaNm'),
                    'post_no': value_or_default(item, 'postNo'),
                    'address': value_or_default(item, 'postNoAdrs'),
                    'phone': value_or_default(item, 'schlRepTpNoCtnt'),
                    'fax': value_or_default(item, 'schlRepFxNoCtnt'),
                    'url': value_or_default(item, 'schlUrlAdrs'),
                    'estb_date': value_or_default(item, 'schlEstbDt'),
                    'lst_updt_dtm': value_or_default(item, 'lstUpdtDtm'),
                })
            log(f'{endpoint["path"]} {school["schl_id"]}/{school["svy_yr"]} {len(items)}건 반영')
            commit_cursor(cur)


def sync_subject_master(cur, endpoints, scope, school_offset=0, school_limit=None):
    schools = load_schools(cur, scope=scope)
    if not schools:
        raise RuntimeError('school_list가 비어 있습니다. 먼저 sync-school-master 실행 필요')
    schools = slice_schools(schools, school_offset=school_offset, school_limit=school_limit)

    for endpoint in endpoints:
        for school in schools:
            params = {
                'serviceKey': common.SERVICE_KEY,
                'svyYr': school['svy_yr'],
                'schlId': school['schl_id'],
            }
            if 'schlKrnNm' in endpoint['required_params']:
                params['schlKrnNm'] = school['name']
            items = fetch_pages(endpoint, params, 'sync_subject_master')

            if endpoint['path'] == '/getUniversityMajorCode':
                for item in items:
                    subject_seed_from_major_code(cur, item)
            else:
                for item in items:
                    subject_merge_from_school_major_info(cur, school['schl_id'], item)

            log(f'{endpoint["path"]} {school["schl_id"]}/{school["svy_yr"]} {len(items)}건 반영')


def sync_school_indicators(cur, endpoints, scope, school_offset=0, school_limit=None, school_id='', svy_yr='', indicator_code=''):
    schools = load_schools(cur, scope=scope)
    indicator_codes = filter_indicator_codes(load_indicator_codes(cur), indicator_code=indicator_code)
    if not schools:
        raise RuntimeError('school_list가 비어 있습니다. 먼저 sync-school-master 실행 필요')
    schools = filter_schools(schools, school_id=school_id, svy_yr=svy_yr)
    if not schools:
        raise RuntimeError('조건에 맞는 school_list가 없습니다. school_id/svy_yr 확인 필요')
    schools = slice_schools(schools, school_offset=school_offset, school_limit=school_limit)
    batch_context = school_batch_context(
        school_offset=school_offset,
        school_limit=school_limit,
        school_count=len(schools),
    )
    processed_school_count = 0
    skipped_request_count = 0
    log(f'sync-school-indicators batch {batch_context}')

    for endpoint in endpoints:
        for school in schools:
            base_params = {
                'serviceKey': common.SERVICE_KEY,
                'svyYr': school['svy_yr'],
                'schlId': school['schl_id'],
            }
            if 'indctId' in endpoint['required_params']:
                param_sets = [dict(base_params, indctId=code) for code in indicator_codes]
            else:
                param_sets = [base_params]

            for params in param_sets:
                try:
                    items = fetch_pages(endpoint, params, 'sync_school_indicator')
                except HTTPError as exc:
                    if exc.code == 429:
                        skipped_request_count += 1
                        skip_indicator_code = params.get('indctId', '')
                        record_school_indicator_skip(
                            endpoint['path'],
                            school['schl_id'],
                            school['svy_yr'],
                            skip_indicator_code,
                            'HTTP 429',
                        )
                        log(f'{endpoint["path"]} {school["schl_id"]}/{school["svy_yr"]} HTTP 429 - {batch_context} 요청 스킵 후 계속')
                        commit_cursor(cur)
                        time.sleep(SCHOOL_INDICATOR_429_COOLDOWN)
                        continue
                    raise
                for item in items:
                    upsert_school_indicator(cur, endpoint_name(endpoint['path']), item, params)
                log(f'{endpoint["path"]} {school["schl_id"]}/{school["svy_yr"]} {len(items)}건 반영')
                time.sleep(school_indicator_request_delay(endpoint['path']))
            processed_school_count += 1
            commit_cursor(cur)
    log(f'sync-school-indicators batch completed {batch_context} processed_schools={processed_school_count} skipped_requests={skipped_request_count}')


def replay_school_indicator_skips(cur, endpoints, args):
    rows = load_school_indicator_skip_rows(args.skip_tsv)
    rows = dedupe_school_indicator_skip_rows(rows)
    rows = filter_skip_rows(
        rows,
        endpoint_path=args.endpoint_path,
        school_id=args.school_id,
        svy_yr=args.svy_yr,
        indicator_code=args.indicator_code,
    )
    if args.limit is not None and args.limit > 0:
        rows = rows[:args.limit]
    if not rows:
        log('재처리할 skip TSV 대상이 없습니다')
        return

    processed_count = 0
    for row in rows:
        matched_endpoints = [endpoint for endpoint in endpoints if endpoint['path'] == row['endpoint_path']]
        if not matched_endpoints:
            log(f"skip TSV {row['line_no']}행 endpoint 미일치 - 건너뜀: {row['endpoint_path']}")
            continue
        log(
            f"skip replay {processed_count + 1}/{len(rows)} "
            f"{row['endpoint_path']} {row['school_id']}/{row['svy_yr']} indctId={row['indicator_code']}"
        )
        sync_school_indicators(
            cur,
            matched_endpoints,
            args.scope,
            school_id=row['school_id'],
            svy_yr=row['svy_yr'],
            indicator_code=row['indicator_code'],
        )
        processed_count += 1
        commit_cursor(cur)
    log(f'skip replay completed processed={processed_count} requested={len(rows)}')


def sync_regional_indicators(cur, endpoints):
    school_div_codes = load_school_div_codes(cur)
    indicator_codes = load_indicator_codes(cur)
    if not school_div_codes:
        raise RuntimeError('학교구분 코드가 없습니다. 먼저 sync-school-master 또는 sync-code-year 실행 필요')

    for endpoint in endpoints:
        for school_div_cd in school_div_codes:
            base_params = {
                'serviceKey': common.SERVICE_KEY,
                'schlDivCd': school_div_cd,
            }
            if 'indctId' in endpoint['required_params']:
                param_sets = [dict(base_params, indctId=code) for code in indicator_codes]
            else:
                param_sets = [base_params]

            for params in param_sets:
                items = fetch_pages(endpoint, params, 'sync_regional_indicator')
                for item in items:
                    upsert_regional_indicator(cur, endpoint_name(endpoint['path']), item, params)
                log(f'{endpoint["path"]} {school_div_cd} {len(items)}건 반영')


def sync_startup_support(cur, endpoints, scope, school_offset=0, school_limit=None):
    schools = load_schools(cur, scope=scope)
    if not schools:
        raise RuntimeError('school_list가 비어 있습니다. 먼저 sync-school-master 실행 필요')
    schools = slice_schools(schools, school_offset=school_offset, school_limit=school_limit)

    for endpoint in endpoints:
        for school in schools:
            params = {
                'serviceKey': common.SERVICE_KEY,
                'svyYr': school['svy_yr'],
                'schlId': school['schl_id'],
            }
            items = fetch_pages(endpoint, params, 'sync_startup_support')
            for idx, item in enumerate(items, start=1):
                insert_startup_support(cur, endpoint_name(endpoint['path']), item, params, idx)
            log(f'{endpoint["path"]} {school["schl_id"]}/{school["svy_yr"]} {len(items)}건 반영')


def print_plan(endpoints):
    groups = {}
    for endpoint in endpoints:
        group = schedule_group(endpoint)
        groups.setdefault(group, []).append(endpoint['path'])

    print('총 스펙:', len(endpoints))
    for group in ('monthly_metadata', 'weekly_master', 'monthly_statistics', 'manual_review'):
        paths = groups.get(group, [])
        print(f'- {group}: {len(paths)}개')
        for path in paths:
            print(f'  - {path}')


def run_job(args):
    endpoints = parse_api_spec()

    if args.job == 'plan':
        print_plan(endpoints)
        return

    common.ensure_config_loaded()
    ensure_schema()
    con = connect_db(common.DB_NAME)
    try:
        with con.cursor() as cur:
            if args.job == 'sync-code-year':
                sync_metadata(cur, [e for e in endpoints if classify(e) == 'metadata'], args.scope)
            elif args.job == 'sync-school-master':
                sync_school_master(cur, [e for e in endpoints if classify(e) == 'school_master'], args.scope)
            elif args.job == 'sync-subject-master':
                sync_subject_master(
                    cur,
                    [e for e in endpoints if classify(e) == 'subject_master'],
                    args.scope,
                    school_offset=args.school_offset,
                    school_limit=args.school_limit,
                )
            elif args.job == 'sync-school-indicators':
                sync_school_indicators(
                    cur,
                    filter_endpoints([e for e in endpoints if classify(e) == 'school_indicator'], args.endpoint_path),
                    args.scope,
                    school_offset=args.school_offset,
                    school_limit=args.school_limit,
                    school_id=args.school_id,
                    svy_yr=args.svy_yr,
                    indicator_code=args.indicator_code,
                )
            elif args.job == 'replay-school-indicator-skips':
                replay_school_indicator_skips(
                    cur,
                    [e for e in endpoints if classify(e) == 'school_indicator'],
                    args,
                )
            elif args.job == 'sync-regional-indicators':
                sync_regional_indicators(cur, [e for e in endpoints if classify(e) == 'regional'])
            elif args.job == 'sync-startup-support':
                sync_startup_support(
                    cur,
                    [e for e in endpoints if classify(e) == 'startup'],
                    args.scope,
                    school_offset=args.school_offset,
                    school_limit=args.school_limit,
                )
            elif args.job == 'sync-all':
                sync_metadata(cur, [e for e in endpoints if classify(e) == 'metadata'], args.scope)
                sync_school_master(cur, [e for e in endpoints if classify(e) == 'school_master'], args.scope)
                sync_subject_master(
                    cur,
                    [e for e in endpoints if classify(e) == 'subject_master'],
                    args.scope,
                    school_offset=args.school_offset,
                    school_limit=args.school_limit,
                )
                sync_school_indicators(
                    cur,
                    filter_endpoints([e for e in endpoints if classify(e) == 'school_indicator'], args.endpoint_path),
                    args.scope,
                    school_offset=args.school_offset,
                    school_limit=args.school_limit,
                    school_id=args.school_id,
                    svy_yr=args.svy_yr,
                    indicator_code=args.indicator_code,
                )
                sync_regional_indicators(cur, [e for e in endpoints if classify(e) == 'regional'])
                sync_startup_support(
                    cur,
                    [e for e in endpoints if classify(e) == 'startup'],
                    args.scope,
                    school_offset=args.school_offset,
                    school_limit=args.school_limit,
                )
            else:
                raise ValueError(f'알 수 없는 작업: {args.job}')
        con.commit()
    finally:
        con.close()


def build_parser():
    parser = argparse.ArgumentParser(description='academyinfo OpenAPI 수집기')
    parser.add_argument(
        'job',
        choices=[
            'plan',
            'sync-code-year',
            'sync-school-master',
            'sync-subject-master',
            'sync-school-indicators',
            'replay-school-indicator-skips',
            'sync-regional-indicators',
            'sync-startup-support',
            'sync-all',
        ],
        help='실행할 작업',
    )
    parser.add_argument(
        '--scope',
        choices=['latest', 'all'],
        default='latest',
        help='년도 범위',
    )
    parser.add_argument(
        '--school-offset',
        type=int,
        default=0,
        help='학교 배치 시작 위치 (sync-subject-master, sync-school-indicators, sync-startup-support용)',
    )
    parser.add_argument(
        '--school-limit',
        type=int,
        default=None,
        help='학교 배치 크기 (sync-subject-master, sync-school-indicators, sync-startup-support용)',
    )
    parser.add_argument(
        '--school-id',
        default='',
        help='특정 학교 ID만 실행 (주로 sync-school-indicators 복구용)',
    )
    parser.add_argument(
        '--svy-yr',
        default='',
        help='특정 조사연도만 실행 (주로 sync-school-indicators 복구용)',
    )
    parser.add_argument(
        '--endpoint-path',
        default='',
        help='특정 endpoint path만 실행 (예: /getComparisonFullTimeFacultyResearchCrntSt)',
    )
    parser.add_argument(
        '--indicator-code',
        default='',
        help='특정 지표코드만 실행 (sync-school-indicators 복구용)',
    )
    parser.add_argument(
        '--skip-tsv',
        default='',
        help='재처리할 skip TSV 경로 (replay-school-indicator-skips용)',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=0,
        help='재처리할 skip TSV 최대 건수 (replay-school-indicator-skips용)',
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.job == 'replay-school-indicator-skips' and args.skip_tsv == '':
        args.skip_tsv = str(default_school_indicator_skip_tsv())
    run_job(args)


if __name__ == '__main__':
    main()
