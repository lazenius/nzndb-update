# Academyinfo DB 스키마 초안

## 기준

- 기준 문서: `academyinfo/API_SPEC.md`
- 매핑 점검 보고서: `academyinfo/MAPPING_GAP_REPORT.md`
- 기준 목록: `academyinfo/README.md`
- 기준 DB: `ACADEMYINFO_DB`
- 명명 기준은 기존 문서와 동일하게 `*_list`, 공통 `recv_time` 우선 사용
- 필드명은 기존 테이블 스타일 + 원천 API 축약명(`schl_id`, `svy_yr`, `indct_id`)을 혼합 사용

## DB 생성문

```sql
CREATE DATABASE IF NOT EXISTS ACADEMYINFO_DB
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ACADEMYINFO_DB;
```

- 모든 테이블: `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`
- 문자열 필드 기본값은 `NOT NULL default ''` (NULL 허용 없음 원칙)
- `recv_time`은 수집 시각. 갱신 시 `INSERT ... ON DUPLICATE KEY UPDATE recv_time=VALUES(recv_time)` 사용

## 전제

- `career`처럼 이 단계는 **문서 기준 스키마 초안**이다.
- Swagger 기준만으로는 산학협력 7개 API의 상세 필드 확정이 부족하다.
- 따라서 1차는 학교/학과/지표 중심으로 잡고, 산학협력은 확장 테이블로 둔다.

## 명명 규칙

- 코드성 목록: `code_list`
- 년도성 목록: `year_list`
- 학교 기본 마스터: `school_list`
- 학과 기본 마스터: `subject_list`
- 학교별 지표값: `school_indicator_list`
- 지역별 지표값: `regional_indicator_list`
- 산학협력/창업 계열: `startup_support_list`
- 공통 수집시각: `recv_time datetime not null`

---

## 1차 구축 기준

### 1. `code_list`

지역/설립/학교유형/학교종류/계열/학위과정/주야간/학과상태 등 코드성 응답 공용 테이블.

```sql
CREATE TABLE ACADEMYINFO_DB.code_list (
    code_type varchar(30) NOT NULL,
    code varchar(30) NOT NULL,
    name varchar(100) NOT NULL,
    parent_code varchar(30) NOT NULL default '',
    rmk varchar(300) NOT NULL default '',
    recv_time datetime NOT NULL,
    PRIMARY KEY (code_type, code),
    KEY (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

| 필드 | 설명 |
|---|---|
| `code_type` | 코드 그룹 식별자 (아래 표 참조) |
| `code` | `cdid` 등 원천 코드값 |
| `name` | `cdnm` |
| `parent_code` | 상위 코드가 있을 때 사용 |
| `rmk` | 비고. `key_indicator` 코드는 단위값(%, 명, 원 등) 저장 |
| `recv_time` | 수집시각 |

**`code_type` 값 목록 (1차 적재 대상)**

| code_type | 수집 API | 설명 |
|---|---|---|
| `region` | `getCodeByRegion` | 지역 코드 |
| `found` | `getCodeByFound` | 설립유형 코드 |
| `school_type` | `getCodeByType` | 학교유형 코드 |
| `school_kind` | `getCodeByKind` | 학교종류 코드 |
| `key_indicator` | `getKeyIndicatorCode` | 주요지표 코드 (`rmk`=단위) |

```sql
-- code_type 초기값 확인용 INSERT 예시 (실 수집 전 schema 검증용)
INSERT IGNORE INTO ACADEMYINFO_DB.code_list (code_type, code, name, rmk, recv_time)
VALUES ('key_indicator', 'TEST01', '테스트지표', '%', NOW());
```

### 2. `year_list`

조사년도/공시년도 목록 관리.

```sql
CREATE TABLE ACADEMYINFO_DB.year_list (
    year_type varchar(30) NOT NULL,
    year_val char(4) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (year_type, year_val)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

| 필드 | 설명 |
|---|---|
| `year_type` | `notice_svy`(우리대학경쟁력 조사년도), `comparison_pub`(대학비교통계 공시년도) |
| `year_val` | `yearVal` |
| `recv_time` | 수집시각 |

**`year_type` 값 목록 (1차 적재 대상)**

| year_type | 수집 API |
|---|---|
| `notice_svy` | `getNoticeSvyYear` |
| `comparison_pub` | `getComparisonPubYear` |

### 3. `school_list`

대학/전문대학 기본정보 + 대학코드 조회성 응답을 합친 메인 학교 테이블.

```sql
CREATE TABLE ACADEMYINFO_DB.school_list (
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
    KEY (name),
    KEY (region_cd),
    KEY (div_cd),
    KEY (kind_cd),
    KEY (est_cd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

| 필드 | 설명 |
|---|---|
| `schl_id` | 학교 식별자 |
| `svy_yr` | 조사/공시년도 |
| `name` | `schlKrnNm` 또는 `schlNm` |
| `full_name` | `schlFullNm` |
| `name_eng` | `schlEngNm` |
| `div_cd`, `div_name` | 학교구분 코드/명 |
| `kind_cd`, `kind_name` | 학교종류 코드/명 |
| `est_cd`, `est_name` | 설립유형 코드/명 |
| `campus_cd`, `campus_name` | 본분교 구분 |
| `region_cd`, `region_name` | 지역 코드/명 |
| `area_cd`, `area_name` | 표준데이터셋 소재지 코드/명 |
| `post_no`, `address`, `phone`, `fax`, `url` | 기본 연락처/주소 |
| `estb_date` | 설립일 |
| `lst_updt_dtm` | 원천 최종수정시각 |
| `recv_time` | 수집시각 |

**수집/merge 기준**

1. `getUniversityCode`로 코드값 중심 row를 먼저 upsert
2. `getSchoolInfo`로 주소/연락처/영문명/설립일을 같은 `(schl_id, svy_yr)` row에 보완 upsert
3. `getNoticeUniversitySearchList`, `getComparisonUniversitySearchList`는 학교 존재 확인 + 일부 명칭 보정 용도로만 사용

즉 `school_list`는 **단일 API 완결 테이블이 아니라 `(schl_id, svy_yr)` 기준 merge 테이블**로 본다.

### 4. `subject_list`

대학별 학과 기본정보 테이블. 실제 의미는 major list지만 기존 관례에 맞춰 `subject_list` 유지.

```sql
CREATE TABLE ACADEMYINFO_DB.subject_list (
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
    KEY (major_id),
    KEY (name),
    KEY (area_cd),
    KEY (schl_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- KEY (schl_id): 학교별 전체 학과 목록 조회 시 사용 (PK 선두 schl_id와 중복이나 단독 스캔 최적화용)
```

| 필드 | 설명 |
|---|---|
| `schl_mjr_id` | 학교 자체 학과 식별자 (`schlMjrId`) |
| `major_id` | `kediMjrId` |
| `std_major_id` | `stdClftMjrId` |
| `name` | `korMjrNm` |
| `college_name` | `clgNm` |
| `srs_lclft_*` | 표준분류 대계열 코드/명 |
| `srs_mclft_*` | 표준분류 중계열 코드/명 |
| `srs_sclft_*` | 표준분류 소계열 코드/명 |
| `area_*` | 학과 지역/권역 |
| `degree_name` | 학위과정 |
| `lesson_term_name` | 수업연한 |
| `oneself_series_name` | 대학자체계열 |
| `major_char_name` | 학과특성 |
| `major_stat_name` | 학과상태 |
| `entrance_quota` | `eschlPscpNum` |
| `graduate_num` | `grdtNum` |
| `edu_course_text` | 교육과정/교육목표 계열 원문 |
| `employ_path_text` | 진로/취업 설명 원문 |
| `recv_time` | 수집시각 |

- `major_id(kediMjrId)`는 표준 분류 ID라 학교별 row 식별자로 단독 사용하지 않는다.
- `subject_list`의 row 식별자는 `schl_mjr_id`를 우선 사용하고, `major_id`는 표준 분류 조인용 보조키로 둔다.

### 5. `school_indicator_list`

대학비교통계 + 우리대학경쟁력 계열의 학교별 지표값 공용 테이블.

```sql
CREATE TABLE ACADEMYINFO_DB.school_indicator_list (
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
    KEY (schl_id),
    KEY (indct_id),
    KEY (api_id, schl_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

| 필드 | 설명 |
|---|---|
| `api_id` | 엔드포인트명. 예: `getComparisonTuitionCrntSt` |
| `indct_id` | 지표코드 |
| `schl_id` | 학교 식별자 |
| `svy_yr` | 공시년도 |
| `indct_yr` | 지표 기준년도 |
| `apy_yr` | 적용년도 (`getNoticeGraduateEmploymentRate` 계열 중심) |
| `val1`~`val10` | `indctVal*` 계열 공용 수용 컬럼 |
| `avg_val` | `indctAvg` |
| `img_url` | `indctImg` |
| `recv_time` | 수집시각 |

**`api_id` 별 `val*` 매핑 기준**

| API 계열 | val 매핑 | 비고 |
|---|---|---|
| 대학비교통계 (`getComparison*`) | `val1`=`indctVal1` | 대부분 단일값 |
| 우리대학경쟁력 (`getNotice*`) | `val1`=`indctVal1`, `val2`=`indctVal2`, `val3`=`indctVal3`, `val4`=`indctVal4` | 최대 4개 + `avg_val`, `img_url` |
| val5~val10 | 예비 컬럼 | 실응답 확인 후 활성화 |

### 6. `regional_indicator_list`

지역별통계 계열 공용 테이블. API마다 `fieldType*`, `fieldVal*`, 3개년도 비교값 구조가 반복된다.

```sql
CREATE TABLE ACADEMYINFO_DB.regional_indicator_list (
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
    KEY (schl_div_cd),
    KEY (indct_id),
    KEY (api_id, indct_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**응답 패턴 분기 처리**

`regional_indicator_list`는 두 가지 응답 구조를 단일 테이블로 수용한다.

| 패턴 | 대표 API | 주요 응답 필드 | 적재 컬럼 |
|---|---|---|---|
| fieldType/fieldVal | `getRegionalSchoolGroundsAndBdsEnsureRate` 등 | `fieldType1~7`, `fieldVal1~7`, `indctId`, `schlDivCd` | `field_type*`, `field_val*` |
| 3개년도 비교 | `getRegionalBasicPropertiesForProfitBurdenRate` 등 | `indctFirst/Second/ThirdSvyYr`, `indctFirst/Second/ThirdVal`, `indctFirst/Second/ThirdSchlCnt`, `znNm`, `znNmRmk`, `indctId`, `schlDivCd` | `first_svy_yr~third_schl_cnt`, `region_name`=`znNm`, `region_rmk`=`znNmRmk` |

- **fieldType 계열**: 응답에 `znNm`(지역명) 없음 → `region_name=''`로 적재, `field_type*/field_val*` 컬럼 사용
- **3개년도 비교 계열**: `znNm`→`region_name`, `znNmRmk`→`region_rmk`, `first~/second~/third~` 컬럼 사용
- 두 패턴 모두 `indctId`를 응답에 포함하므로 PK의 `indct_id` 구성 유효
- `region_rmk`는 일부 지역통계 API에서 실질 구분자 역할을 할 수 있으므로 PK에 포함한다.

### 7. `startup_support_list`

산학협력/창업지원 7개 API 공용 테이블. 실제 실응답을 본 뒤 분해 가능성이 가장 높다.

```sql
CREATE TABLE ACADEMYINFO_DB.startup_support_list (
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
    KEY (indct_id),
    KEY (item_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

| 필드 | 설명 |
|---|---|
| `api_id` | 산학협력 엔드포인트명 (예: `getContractMajorCrntSt`) |
| `indct_id` | 산학협력 지표 식별자 |
| `indct_yr` | 지표 기준년도 |
| `seq` | 동일 학교/년도 내 행 반복순번. 원천 응답에 순번 없을 시 수집 루프에서 1부터 부여 |
| `item_key` | 원천 응답 필드명 (카멜케이스 그대로 사용 가능) |
| `item_value` | 원천 응답 값 (varchar 300) |
| `recv_time` | 수집시각 |

**산학협력 7개 API → `api_id` 값 목록**

| api_id | API 설명 |
|---|---|
| `getContractMajorCrntSt` | 계약학과 현황 |
| `getOrderMadeCourseCrntSt` | 주문식 교육과정 현황 |
| `getFieldPracticeCourseCrntSt` | 현장실습 교과목 현황 |
| `getCapstoneDesignCourseCrntSt` | 캡스톤디자인 교과목 현황 |
| `getTeacherStartupCrntSt` | 교수 창업 현황 |
| `getStudentStartupCrntSt` | 학생 창업 현황 |
| `getStartupEducationCrntSt` | 창업교육 현황 |

> api_id 명칭은 Swagger 미확인 상태로 추정값. 실응답 확인 후 확정.

---

## 2차 확장 권장

### 1. `school_indicator_value_list`

`val1`~`val10` 고정 컬럼이 답답하면 `value_no`, `value_name`, `value` 구조로 세로 분해.

### 2. `startup_*_list`

산학협력 7개 API는 실응답 확보 뒤 아래처럼 분리 가능.

- `contract_major_list`
- `ordermade_course_list`
- `field_practice_list`
- `capstone_design_list`
- `teacher_startup_list`
- `student_startup_list`
- `startup_education_list`

---

## 우선 구현 기준 정리

**1단계 — 마스터/코드 (의존성 없음, 가장 먼저)**

| 순번 | 테이블 | 수집 API | 비고 |
|---|---|---|---|
| 1 | `code_list` | `getCodeByRegion`, `getCodeByFound`, `getCodeByType`, `getCodeByKind`, `getKeyIndicatorCode` | 코드 확보 후 2단계 진행 |
| 2 | `year_list` | `getNoticeSvyYear`, `getComparisonPubYear` | 유효 년도 확정 |

**2단계 — 학교/학과 마스터**

| 순번 | 테이블 | 수집 API |
|---|---|---|
| 3 | `school_list` | `getSchoolInfo`, `getUniversityCode` |
| 4 | `subject_list` | `getSchoolMajorInfo` |

**3단계 — 지표/통계 (2단계 완료 후)**

| 순번 | 테이블 | 수집 API 계열 |
|---|---|---|
| 5 | `school_indicator_list` | 대학비교통계(`getComparison*`), 우리대학경쟁력(`getNotice*`) |
| 6 | `regional_indicator_list` | 지역별통계(`getRegional*`) |

**4단계 — 산학협력 (실응답 확인 후)**

| 순번 | 테이블 | 비고 |
|---|---|---|
| 7 | `startup_support_list` | KV 임시 적재 → 실응답 후 세부 테이블 분해 결정 |

## 리스크

- `getSchoolInfo`, `getSchoolMajorInfo`는 표준데이터셋 성격이라 필드가 비교적 안정적이다.
- 지역별통계/우리대학경쟁력은 `fieldType*`, `indctVal*`처럼 화면 지향 응답이 섞여 있어 컬럼 재분해가 필요할 수 있다.
- 산학협력 7종은 Swagger만으로는 컬럼 확정 근거가 부족해 1차는 보수적으로 설계했다.
- `regional_indicator_list`의 fieldType 패턴 API는 `region_name=''`로 적재되므로 PK 충돌 없으나, 같은 `api_id+indct_id+schl_div_cd`에 여러 행이 와야 할 경우 `region_name` 컬럼에 대체 구분자 필요.
- `startup_support_list`의 `api_id` 값은 Swagger에서 직접 확인 필요 (현재 추정값 사용).
