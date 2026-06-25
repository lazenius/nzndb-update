# Career DB 스키마 초안

## 기준

- 기준 문서: `career/openAPI이용매뉴얼_v4.1.pdf`
- 기준 코드: 서버 `/var/www/html/update/career/*.py`
- 기준 DB: `CAREER_DB`
- 명명 기준은 **현재 운영 중인 테이블명/필드명 우선** 사용

## 명명 규칙

- 목록성 마스터는 기존대로 `*_list`
  - 예: `job_list`, `school_list`, `subject_list`, `code_list`
- 기본 식별자는 기존 필드명 유지
  - 직업: `code`
  - 학교/학과: `school`, `seq`
  - 공통 수집시각: `recv_time`
- 코드성 필드는 기존처럼 `char(6)` 유지
  - `std_code`, `emp_code`, `apt_code`, `thm_code`, `cat_code`, `sch1`, `sch2`, `region`, `est`, `faculty`
- 상세/반복 데이터는 부모 키 + 반복 순번 또는 구분값으로 분리 저장

---

## 1차 구축 기준: 현재 운영 중 테이블

### 1. `code_list`

직업 표준코드, 고용코드, 기타 코드값 공용 테이블.

```sql
CREATE TABLE CAREER_DB.code_list (
    code char(6) NOT NULL,
    name varchar(50) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (code)
);
```

| 필드 | 타입 | 설명 |
|---|---|---|
| `code` | `char(6)` | 코드값 |
| `name` | `varchar(50)` | 코드명 |
| `recv_time` | `datetime` | 수집시각 |

### 2. `job_list`

직업백과 목록 + 상세 `baseInfo` 기준 메인 테이블.

```sql
CREATE TABLE CAREER_DB.job_list (
    code int unsigned NOT NULL,
    name varchar(100) NOT NULL,
    std_code char(6) NOT NULL,
    emp_code char(6) NOT NULL,
    apt_code char(6) NOT NULL,
    thm_code char(6) NOT NULL,
    cat_code char(6) NOT NULL,
    related_job varchar(300) NOT NULL,
    social varchar(10) NOT NULL,
    balance varchar(10) NOT NULL,
    satisfication decimal(4,1) unsigned NOT NULL,
    wage int unsigned NOT NULL,
    edit_date date NOT NULL,
    reg_date date NOT NULL,
    views int unsigned NOT NULL,
    likes int unsigned NOT NULL,
    tag varchar(300) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (code),
    KEY (name),
    KEY (apt_code),
    KEY (thm_code),
    KEY (cat_code)
);
```

| 필드 | 설명 |
|---|---|
| `code` | 직업코드 (`job_cd`) |
| `name` | 직업명 (`job_nm`) |
| `std_code` | 표준직업코드 |
| `emp_code` | 고용코드 |
| `apt_code` | 적성유형 코드 |
| `thm_code` | 테마 코드 |
| `cat_code` | 직업분류 코드 |
| `related_job` | 관련직업명 |
| `social` | 사회공헌 |
| `balance` | 일가정균형 |
| `satisfication` | 직업만족도 |
| `wage` | 평균연봉 |
| `edit_date` | 수정일 |
| `reg_date` | 등록일 |
| `views` | 조회수 |
| `likes` | 추천수 |
| `tag` | 태그 원문 |
| `recv_time` | 수집시각 |

### 3. `school_list`

학교정보 목록 테이블.

```sql
CREATE TABLE CAREER_DB.school_list (
    school char(4) NOT NULL,
    seq int unsigned NOT NULL,
    name varchar(50) NOT NULL,
    campus varchar(50) NOT NULL,
    sch1 char(6) NOT NULL,
    sch2 char(6) NOT NULL,
    region char(6) NOT NULL,
    est char(6) NOT NULL,
    address varchar(200) NOT NULL,
    link varchar(300) NOT NULL,
    info varchar(300) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (school, seq),
    KEY (name)
);
```

| 필드 | 설명 |
|---|---|
| `school` | 학교구분 축약값 (`elem`, `midd`, `high`, `univ`, `seet`, `alte`) |
| `seq` | 학교 고유번호 |
| `name` | 학교명 |
| `campus` | 캠퍼스명 |
| `sch1` | 학교유형 1 코드 |
| `sch2` | 학교유형 2 코드 |
| `region` | 지역 코드 |
| `est` | 설립유형 코드 |
| `address` | 주소 |
| `link` | 학교 링크 |
| `info` | mycollege 링크 등 부가 링크 |
| `recv_time` | 수집시각 |

### 4. `subject_list`

학과정보 목록 테이블. 실제 의미는 `major list`지만 기존 명칭 따라 `subject_list` 유지.

```sql
CREATE TABLE CAREER_DB.subject_list (
    school char(4) NOT NULL,
    seq int unsigned NOT NULL,
    name varchar(30) NOT NULL,
    faculty char(6) NOT NULL,
    others varchar(3000) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (school, seq),
    KEY (name)
);
```

| 필드 | 설명 |
|---|---|
| `school` | `high` / `univ` |
| `seq` | 학과코드 (`majorSeq`) |
| `name` | 학과명 (`mClass`) |
| `faculty` | 계열 코드 (`lClass`) |
| `others` | 세부학과명(`facilName`) 원문 |
| `recv_time` | 수집시각 |

---

## 2차 확장 권장: 직업 상세 API

직업 상세는 반복 노드가 많아서 `job_list` 1개로 끝내면 비정규화 심함. 기존 서버 코드 주석안도 이 방향.

### 1. `job_work_list`

```sql
CREATE TABLE CAREER_DB.job_work_list (
    jcode int unsigned NOT NULL,
    seq tinyint unsigned NOT NULL,
    work varchar(1000) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode, seq)
);
```

### 2. `interest_list`

```sql
CREATE TABLE CAREER_DB.interest_list (
    jcode int unsigned NOT NULL,
    seq tinyint unsigned NOT NULL,
    interest varchar(3000) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode, seq)
);
```

### 3. `research_list`

```sql
CREATE TABLE CAREER_DB.research_list (
    jcode int unsigned NOT NULL,
    seq tinyint unsigned NOT NULL,
    research varchar(3000) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode, seq)
);
```

### 4. `job_ready_list`

`jobReadyList`는 1:1 묶음이라 한 테이블로 유지.

```sql
CREATE TABLE CAREER_DB.job_ready_list (
    jcode int unsigned NOT NULL,
    recruit varchar(3000) NOT NULL,
    certificate varchar(3000) NOT NULL,
    training varchar(3000) NOT NULL,
    curriculum varchar(3000) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode)
);
```

### 5. `forecast_list`

```sql
CREATE TABLE CAREER_DB.forecast_list (
    jcode int unsigned NOT NULL,
    forecast varchar(3000) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode)
);
```

### 6. `edu_chart`

```sql
CREATE TABLE CAREER_DB.edu_chart (
    jcode int unsigned NOT NULL,
    chart_name varchar(100) NOT NULL,
    chart_data varchar(200) NOT NULL,
    source varchar(300) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode)
);
```

### 7. `perform_list`

`environment`, `perform`, `knowledge` 구조가 같으므로 하나로 통합 권장.

```sql
CREATE TABLE CAREER_DB.perform_list (
    jcode int unsigned NOT NULL,
    area enum('environment','perform','knowledge') NOT NULL,
    seq tinyint unsigned NOT NULL,
    name varchar(100) NOT NULL,
    inform varchar(1000) NOT NULL,
    importance tinyint unsigned NOT NULL,
    source varchar(300) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode, area, seq),
    KEY (name)
);
```

### 8. `major_chart`

직업별 관련 전공 분포.

```sql
CREATE TABLE CAREER_DB.major_chart (
    jcode int unsigned NOT NULL,
    major varchar(100) NOT NULL,
    major_data varchar(200) NOT NULL,
    source varchar(300) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode)
);
```

### 9. `ability_list`

```sql
CREATE TABLE CAREER_DB.ability_list (
    jcode int unsigned NOT NULL,
    sort_ordr char(2) NOT NULL,
    ability_name varchar(50) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode, sort_ordr),
    KEY (ability_name)
);
```

### 10. `depart_list`

```sql
CREATE TABLE CAREER_DB.depart_list (
    jcode int unsigned NOT NULL,
    depart_id int unsigned NOT NULL,
    depart_name varchar(100) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode, depart_id),
    KEY (depart_name)
);
```

### 11. `rel_sol_list`

관련 상담 사례.

```sql
CREATE TABLE CAREER_DB.rel_sol_list (
    jcode int unsigned NOT NULL,
    cnslt_seq int unsigned NOT NULL,
    trget_se varchar(50) NOT NULL,
    sj varchar(300) NOT NULL,
    cn text NOT NULL,
    regist_dt date NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode, cnslt_seq)
);
```

### 12. `tag_list`

```sql
CREATE TABLE CAREER_DB.tag_list (
    jcode int unsigned NOT NULL,
    seq tinyint unsigned NOT NULL,
    tag varchar(50) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode, seq),
    KEY (tag)
);
```

### 13. `job_rel_org_list`

```sql
CREATE TABLE CAREER_DB.job_rel_org_list (
    jcode int unsigned NOT NULL,
    seq tinyint unsigned NOT NULL,
    rel_org varchar(100) NOT NULL,
    rel_org_url varchar(300) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode, seq)
);
```

### 14. `indicator_chart`

```sql
CREATE TABLE CAREER_DB.indicator_chart (
    jcode int unsigned NOT NULL,
    indicator varchar(200) NOT NULL,
    indicator_data varchar(200) NOT NULL,
    source varchar(300) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (jcode)
);
```

---

## 2차 확장 권장: 학과 상세 API

학과 상세는 현재 운영 테이블 없음. 다만 기존 명명 규칙 따라 `subject_*` 접두사 유지 권장.

### 1. `subject_detail_list`

학과 상세 1:1 본문.

```sql
CREATE TABLE CAREER_DB.subject_detail_list (
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
);
```

메모
- 대학은 `salary`, `employment`, `qualifications`, `property` 사용
- 고등학교는 `purpose`, `relatedjob` 사용
- 없는 값은 빈 문자열 저장

### 2. `subject_text_list`

반복 텍스트 묶음 공통 저장.

```sql
CREATE TABLE CAREER_DB.subject_text_list (
    school char(4) NOT NULL,
    seq int unsigned NOT NULL,
    section varchar(30) NOT NULL,
    item_seq smallint unsigned NOT NULL,
    item_name varchar(100) NOT NULL,
    item_desc text NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (school, seq, section, item_seq)
);
```

`section` 예시
- `relate_subject`
- `career_act`
- `enter_field`
- `main_subject`

### 3. `subject_school_map`

개설 학교/설치 학교 매핑.

```sql
CREATE TABLE CAREER_DB.subject_school_map (
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
    KEY (school_name)
);
```

### 4. `subject_chart_list`

입학상황/취업률/만족도 등 차트 공통 저장.

```sql
CREATE TABLE CAREER_DB.subject_chart_list (
    school char(4) NOT NULL,
    seq int unsigned NOT NULL,
    chart_type varchar(30) NOT NULL,
    item_seq smallint unsigned NOT NULL,
    item_name varchar(100) NOT NULL,
    item_label varchar(100) NOT NULL,
    item_value varchar(50) NOT NULL,
    recv_time datetime NOT NULL,
    PRIMARY KEY (school, seq, chart_type, item_seq)
);
```

`chart_type` 예시
- `applicant`
- `gender`
- `employment_rate`
- `field`
- `avg_salary`
- `satisfaction`
- `after_graduation`
- `graduation_gender`

### 5. `subject_feature_list`

많이본/관심직업 특성 데이터 공통 저장.

```sql
CREATE TABLE CAREER_DB.subject_feature_list (
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
);
```

`feature_group` 예시
- `GenCD`
- `SchClass`
- `lstMiddleAptd`
- `lstHighAptd`
- `lstVals`

`feature_type`
- `popular`
- `bookmark`

---

## 구현 우선순위

### 우선 1
- `code_list`
- `job_list`
- `school_list`
- `subject_list`

### 우선 2
- `job_work_list`
- `job_ready_list`
- `forecast_list`
- `perform_list`
- `subject_detail_list`
- `subject_chart_list`

### 우선 3
- `interest_list`
- `research_list`
- `major_chart`
- `ability_list`
- `depart_list`
- `rel_sol_list`
- `tag_list`
- `job_rel_org_list`
- `indicator_chart`
- `subject_text_list`
- `subject_school_map`
- `subject_feature_list`

---

## 수집기 구현 범위

### 1차 구현 대상

문서/예제 기준으로 우선 구현 범위는 **직업 목록 → 직업 상세 → 코드표 동기화**까지만 잡는다.
학교/학과 API는 현재 스키마 기준만 확정하고 실제 수집기는 2차로 넘긴다.

### 직업 목록 수집기

- 엔드포인트: `https://www.career.go.kr/cnet/front/openapi/jobs.json`
- 예제 호환 엔드포인트: `https://www.career.go.kr/cnet/openapi/getOpenApi`
- 필수 파라미터: `apiKey`
- 선택 파라미터:
  - `pageIndex`
  - `searchJobNm`
  - `searchAptdCodes`
  - `searchThemes`
  - `searchJobCd`
- 예제 호환 파라미터:
  - `svcType=api`
  - `svcCode=JOB`
  - `contentType=json`
  - `gubun=job_dic_list`
- 적재 대상:
  - `job_list`
- 수집 단위:
  - 목록 응답에서 `seq` 또는 `jobdicSeq` 계열 직업 식별자 확보
  - 메인 메타 필드 우선 적재
  - 상세 수집 대상 키 큐 생성

### 직업 상세 수집기

- 엔드포인트: `https://www.career.go.kr/cnet/front/openapi/job.json`
- 예제 호환 엔드포인트: `https://www.career.go.kr/cnet/openapi/getOpenApi`
- 필수 파라미터:
  - `apiKey`
  - `seq`
- 예제 호환 파라미터:
  - `svcType=api`
  - `svcCode=JOB_VIEW`
  - `contentType=json`
  - `gubun=job_dic_list`
  - `jobdicSeq`
- 적재 대상:
  - `job_list` 보강
  - `job_work_list`
  - `interest_list`
  - `research_list`
  - `job_ready_list`
  - `forecast_list`
  - `edu_chart`
  - `perform_list`
  - `major_chart`
  - `ability_list`
  - `depart_list`
  - `rel_sol_list`
  - `tag_list`
  - `job_rel_org_list`
  - `indicator_chart`
- 구현 메모:
  - 상세 응답의 반복 노드는 테이블별 upsert 대신 `직업코드 전체 삭제 후 재적재`가 단순하다
  - 문자열 `"null"` 과 실제 `null` 을 구분해 빈 문자열 처리 규칙을 고정해야 한다
  - 차트계 데이터는 원문 순서를 보존해야 재수집 비교가 쉽다
  - HTML 예제의 `stateofemp` 는 위치 기반 배열 접근이라 실제 운영 응답 구조 재확인이 필요하다

### 코드표 수집기

- 엔드포인트:
  - `https://www.career.go.kr/cnet/front/openapi/themes.json`
  - `https://www.career.go.kr/cnet/front/openapi/aptds.json`
  - `https://www.career.go.kr/cnet/front/openapi/jobcodes.json`
- 적재 대상:
  - `code_list`
- 구현 메모:
  - 코드 출처 구분 컬럼은 아직 추가하지 않고 기존 `code_list` 구조 유지
  - 코드 충돌 여부는 실제 응답 확인 후 판단

### 2차 구현 대상

- 학교 목록 수집기
- 학과 목록 수집기
- 학과 상세 수집기
- 진로상담/교육자료 연계 수집기

---

## 검증 계획

### 1. 스키마 검증

- 모든 `CREATE TABLE` 문이 MariaDB/MySQL에서 실행되는지 확인
- 기본키/보조키 이름 충돌 없는지 확인
- 기존 운영 명칭(`job_list`, `subject_list`, `code_list`) 유지 여부 확인

### 2. API 응답 매핑 검증

- `jobs.json` 샘플 1건으로 `job_list` 필드 매핑표 작성
- `job.json` 샘플 1건으로 반복 노드별 대상 테이블 매핑표 작성
- 누락 필드/이름 차이(`seq`, `job_cd`, `jobdicSeq` 등) 확인

### 3. 적재 로직 검증

- 동일 직업 1건 재수집 시 중복행이 생기지 않아야 함
- 상세 반복 테이블은 재수집 후 행 수가 원본과 일치해야 함
- 빈 배열/누락 노드 응답에서도 적재기가 중단되지 않아야 함

### 4. 운영 전 점검

- API 키 실패/호출 제한 응답 처리 방식 확인
- 일 배치 기준 예상 호출 수 산정
- `recv_time` 기준 증분 검증 가능 여부 확인

### 검증 순서

1. SQL 실행 검증
2. 목록 API 샘플 저장
3. 상세 API 샘플 저장
4. 샘플 JSON 기준 필드 매핑표 확정
5. 수집기 구현
6. 동일 샘플 재적재 회귀 확인

---

## 작업 순서

1. `code_list`, `job_list` 기준 SQL 확정
2. 목록/상세 샘플 응답 원본 저장
3. `job_list` 1차 적재기 구현
4. 상세 반복 테이블 분리 적재기 구현
5. 코드표 동기화 추가
6. 재수집/중복/빈값 케이스 검증
7. 이후 학교/학과 API 범위로 확장

---

## 결정

- `major` 대신 기존 운영 명칭 따라 `subject` 유지
- 공통 코드 테이블은 새로 쪼개지 않고 `code_list` 재사용
- 상세 API 반복 노드는 가능하면 1:N 분리
- `recv_time` 전 테이블 공통 유지
- 원문 필드는 당분간 텍스트 보존 우선, 가공 컬럼 추가는 나중
