# update / robocode-admin 분업 기준

## 목적

- `update` 와 `robocode-admin` 의 책임을 섞지 않고, 이후 작업 위치를 명확히 한다.

## 원칙

| 영역 | 경로 | 책임 |
|---|---|---|
| 수집/적재 | `/var/www/html/update` | OpenAPI 수집기, DB 구축, cron, 적재 검증 |
| 모니터링 | `/var/www/html/robocode-admin/db/` | DB 상태 조회, 최근 적재 결과, 에러 확인용 PHP 페이지 |
| 사용자 기능 | 별도 웹 영역 | 적성검사 같은 실시간 사용 페이지 |

---

## 1. update 프로젝트에서 계속 할 일

### Career
- 직업/코드/학교/학과 수집기 완성
- 상세 테이블 확장 여부 결정
- 적성검사 API는 DB 적재보다 운영 로그 기준 우선 정리

### Academyinfo
- 학교/학과/지표 적재 안정화
- 산학협력 7개 스펙 정규화 여부 결정
- 배치/cron 운영 안정화

### 공통
- cron 등록 및 실행 주기 문서화
- 최근 적재 건수 검증
- 장애 시 재실행 기준 정리

---

## 2. robocode-admin/db/ 에서 만들 화면


## 2-1. 2026-06-27 서버 확인 메모

- `/var/www/html/robocode-admin` 저장소는 존재하고, 현재는 `config/bootstrap.php`, `index.php`, `public/.htaccess`만 있는 **초기 스켈레톤** 상태다.
- `/var/www/html/robocode-admin/db/` 는 아직 비어 있으므로, 1차 구현은 이 경로에 새로 만든다.
- PHP 8.2 + `mysqli`/`pdo_mysql` 사용 가능.
- 기존 `nznlab/db/mysql/*.inc` 는 구형 계층 흔적이 있지만, 장기적으로는 `nznlab/db/career`, `nznlab/db/academyinfo` 에 **스펙별 조회 함수**를 두고 `robocode-admin/db/` 는 이를 호출하는 얇은 화면 계층으로 되돌리는 것이 맞다. 현재 `robocode-admin/db/` 직접 SQL 은 1차 운영 확인용 임시 구현으로 본다.


### 최소 1차 화면

| 페이지 | 목적 |
|---|---|
| `career_status.html` | career 수집 테이블별 건수/최근 갱신시각 확인 |
| `academyinfo_status.html` | academyinfo 수집 테이블별 건수/최근 갱신시각 확인 |
| `collector_runs.html` | 최근 실행 로그/성공실패 확인 |


### 추가 1차 조회 화면

| 페이지 | 목적 |
|---|---|
| `specs.php` | `academyinfo` / `career` 전체 스펙 상태표를 문서 기준으로 그대로 확인 |
| `schools.php` | 학교명 검색, 도메인별 최신 학교 적재 결과 조회 |
| `subjects.php` | 학과명 검색, 도메인별 최신 학과 적재 결과 조회 |

### 1차 데이터 소스 정의

| 페이지 | 주 조회 대상 | 최소 확인 항목 |
|---|---|---|
| `career_status.html` | `code_list`, `job_list`, `school_list`, `subject_list`, `subject_detail_list` | 테이블별 건수, 최근 `recv_time`, 마지막 성공 로그 파일명 |
| `academyinfo_status.html` | `year_list`, `school_list`, `subject_list`, `school_indicator_list`, `regional_indicator_list`, `startup_support_list` | 테이블별 건수, 최신 년도, 최근 `recv_time`, 최근 배치 로그 |
| `collector_runs.html` | `update` 각 수집기 로그 파일 | 작업명, 시작시각, 종료시각, 성공/실패, 429 여부 |

### 1차 후속 정의

- `update` 쪽에서 제공해야 할 기준
  - 테이블별 최근 적재시각을 뽑을 수 있는 SQL
  - 수집기별 로그 파일 경로 규칙
  - `HTTP 429` 같은 운영 경고를 문자열 검색으로 잡을지, 별도 실행 이력 테이블로 뽑을지 결정
  - 상세 계약 문서: `UPDATE_MONITORING_DATA_CONTRACT.md`
- `robocode-admin` 쪽에서 바로 만들 수 있는 범위
  - 읽기 전용 PHP 조회
  - 최근 로그 tail 요약
  - 수동 새로고침형 상태 표

### 1차 디자인 원칙

- 디자인 불필요
- 표 중심
- 수동 새로고침 기준
- 관리자 1인 확인용
- 외부 접근 페이지는 `.html`
- 내부 데이터 처리 프로그램은 `.php`

---

## 2-2. 조회 계층 정리 방향

- 예전 운영 방식 기준으로는 `nznlab/db/career`, `nznlab/db/academyinfo` 아래에 도메인별 조회 함수를 두는 편이 자연스럽다.
- 권장 책임 분리
  - `update`: 수집/적재/cron/로그
  - `nznlab/db/*`: 학교/학과/상태 집계 조회 함수
  - `robocode-admin/db/*`: GET 파라미터 수신 + 표 렌더
- 따라서 현재 `robocode-admin/db/*.php` 안의 직접 SQL 은 점진적으로 `nznlab/db/*` 로 올려서 재사용 가능하게 정리한다.

### 조회 라이브러리 파일명/함수명 규칙 초안

- 디렉터리
  - `nznlab/db/academyinfo/`
  - `nznlab/db/career/`
- 파일명
  - 화면 기준이 아니라 **조회 주제 기준**으로 나눈다.
  - 예: `schools.inc`, `subjects.inc`, `status.inc`
- 함수명
  - 도메인 접두어 + 조회 대상 + 동작 형태로 단순하게 맞춘다.
  - 예: `academyinfo_get_schools()`, `academyinfo_get_subjects()`, `academyinfo_get_status_rows()`
  - 예: `career_get_schools()`, `career_get_subjects()`, `career_get_status_rows()`
- 파라미터
  - 화면 `$_GET` 을 직접 받지 않고, 검색어/limit/offset 같은 값만 인자로 받는다.
- 반환값
  - `mysqli` result 를 그대로 넘기지 말고, 화면에서 바로 쓸 수 있는 배열 형태로 맞춘다.
- 범위
  - 1차 이관 대상은 `schools.php`, `subjects.php`, `career_status.php`, `academyinfo_status.php` 에 들어간 조회 SQL 로 한정한다.

### 1차 이관 대상 공통 조회 함수 목록

- `schools.php` 에서 분리
  - `academyinfo_get_schools($keyword = '', $limit = 100, $offset = 0)`
  - `career_get_schools($keyword = '', $limit = 100, $offset = 0)`
- `subjects.php` 에서 분리
  - `academyinfo_get_subjects($keyword = '', $limit = 100, $offset = 0)`
  - `career_get_subjects($keyword = '', $limit = 100, $offset = 0)`
- `career_status.php` 에서 분리
  - `career_get_status_rows()`
- `academyinfo_status.php` 에서 분리
  - `academyinfo_get_status_rows()`
- 필요 시 공통 보조 함수
  - `db_fetch_all($sql)` 같은 범용 함수는 `nznlab/db/mysql` 공통부 또는 각 도메인 `common.inc` 에 둔다.
  - 화면 정렬/출력 포맷 로직은 `robocode-admin/db` 에 남긴다.

### 조회 라이브러리 ↔ 페이지 연결 기준

| 페이지 | 우선 호출 라이브러리 | 최소 진입 함수 | 비고 |
|---|---|---|---|
| `robocode-admin/db/career_status.php` | `nznlab/db/career/status.inc` | `career_get_status_rows()` | 표 렌더만 페이지에 남긴다. |
| `robocode-admin/db/academyinfo_status.php` | `nznlab/db/academyinfo/status.inc` | `academyinfo_get_status_rows()` | `school_indicator_list` 비고 규칙까지 포함한다. |
| `robocode-admin/db/schools.php` | `nznlab/db/career/schools.inc`, `nznlab/db/academyinfo/schools.inc` | `career_get_schools()`, `academyinfo_get_schools()` | `all` 병합/정렬은 페이지 책임이다. |
| `robocode-admin/db/subjects.php` | `nznlab/db/career/subjects.inc`, `nznlab/db/academyinfo/subjects.inc` | `career_get_subjects()`, `academyinfo_get_subjects()` | 검색 파라미터 정규화는 페이지에서 한다. |
| `robocode-admin/db/collector_runs.php` | 직접 로그 요약 또는 추후 `nznlab/db/*/status.inc` 보조 함수 | 미정 | 1차는 직접 로그 tail 허용, SQL 집계와 섞지 않는다. |

- 1차 기준에서 `status.inc`, `schools.inc`, `subjects.inc` 는 **도메인별 조회 전용**으로 유지한다.
- `robocode-admin/db/*.php` 는 `$_GET` 정리, 호출 분기, HTML 출력만 담당한다.
- `update` 저장소는 위 함수가 참조할 SQL/로그 계약만 보증하고, 화면 구현 자체는 담당하지 않는다.

### `schools.php` 1차 SQL 이관 스케치

- `robocode-admin/db/schools.php` 에 남길 것
  - `domain`, `q`, `limit`, `offset` 같은 요청값 정리
  - `academyinfo`, `career`, `all` 분기
  - 최종 표 컬럼 정의와 출력
- `nznlab/db/academyinfo/schools.inc` 로 옮길 것
  - `academyinfo_get_schools($keyword = '', $limit = 100, $offset = 0)`
  - 대상 테이블: `ACADEMYINFO_DB.school_list`
  - 기본 반환 컬럼: `schl_id`, `name`, `full_name`, `region_name`, `kind_name`, `url`, `recv_time`
- `nznlab/db/career/schools.inc` 로 옮길 것
  - `career_get_schools($keyword = '', $limit = 100, $offset = 0)`
  - 대상 테이블: `CAREER_DB.school_list`
  - 기본 반환 컬럼: `school`, `seq`, `name`, `campus`, `region`, `est`, `link`, `recv_time`
- `all` 병합 규칙
  - 두 함수는 각각 배열 반환
  - 병합/정렬(`recv_time desc`)은 `schools.php` 에 남긴다.
- 1차 목표
  - 화면 HTML 은 그대로 두고, `schools.php` 에서 SQL 문자열만 제거한다.

## 3. 데이터 연결 기준

`robocode-admin/db/` 페이지는 `update` DB를 읽기만 한다.

즉:
- 쓰기/수집/정제 로직은 `update`
- 보기/확인/점검 로직은 `robocode-admin`

---

## 4. 적성검사 API의 위치

- 적성검사 API는 `update` 의 정기수집 대상이 아니라 **사용자 상호작용 기능**에 가깝다.
- 따라서 본체 페이지는 `robocode-admin` 이 아니라 별도 사용자 웹 영역이 더 맞다.
- 다만 운영 관점의 호출 성공/실패 현황은 `robocode-admin/db/` 에서 확인 가능해야 한다.

---

## 5. robocode-admin 모니터링 1차 후속 정의

1. `update` 에서 career/academyinfo 미구현 수집기 정리
2. `update` DB 기준 모니터링용 SQL/로그 경로 규칙 확정
3. `robocode-admin/db/` 에 단순 PHP 상태 페이지 생성
4. 적성검사 사용자 페이지는 별도 웹 영역에서 구현

---

## 6. 모니터링 1차 후속 정의

### `career_status.html`

- 최소 표:
  - `code_list`
  - `job_list`
  - `school_list`
  - `subject_list`
  - `subject_detail_list`
- 최소 컬럼:
  - 테이블명
  - 행 수
  - 최근 `recv_time`
  - 비고(예: cron 등록 여부)
- 목적:
  - `sync-school-list`, `sync-subject-list` 가 정기 운영 편입됐는지 빠르게 확인

### `academyinfo_status.html`

- 최소 표:
  - `code_list`
  - `year_list`
  - `school_list`
  - `subject_list`
  - `school_indicator_list`
  - `regional_indicator_list`
  - `startup_support_list`
- 최소 컬럼:
  - 테이블명
  - 행 수
  - 최근 `recv_time`
  - 최근 대상 연도 또는 비고
- 목적:
  - `school_indicator_list` 의 분할 배치 운영과 `startup_support_list` 적재 상태를 함께 확인

### `collector_runs.html`

- 최소 소스:
  - `career/logs/*.log`
  - `academyinfo/logs/*.log`
- 최소 컬럼:
  - 작업명
  - 마지막 실행시각
  - 성공/실패 추정
  - 마지막 의미 있는 로그 1줄
- 특히 보여줄 항목:
  - `academyinfo sync_school_indicator*` 의 마지막 offset 범위
  - `HTTP 429` 발생 여부
  - `career sync-school-list`, `sync-subject-list` 정기 실행 유무

## 7. robocode-admin 1차 데이터 계약 고정

### SQL 기준

#### `career_status.html`

```sql
SELECT 'code_list' AS table_name, COUNT(*) AS row_count, MAX(recv_time) AS last_recv_time
FROM CAREER_DB.code_list
UNION ALL
SELECT 'job_list', COUNT(*), MAX(recv_time)
FROM CAREER_DB.job_list
UNION ALL
SELECT 'school_list', COUNT(*), MAX(recv_time)
FROM CAREER_DB.school_list
UNION ALL
SELECT 'subject_list', COUNT(*), MAX(recv_time)
FROM CAREER_DB.subject_list;
```

- cron 비고는 SQL이 아니라 운영 메모 컬럼으로 고정한다.
- `school_list`, `subject_list` 는 최근 성공 로그 파일명을 함께 붙여서 본다.

#### `academyinfo_status.html`

```sql
SELECT 'year_list' AS table_name, COUNT(*) AS row_count, MAX(year_val) AS latest_year, MAX(recv_time) AS last_recv_time
FROM ACADEMYINFO_DB.year_list
UNION ALL
SELECT 'school_list', COUNT(*), MAX(svy_yr), MAX(recv_time)
FROM ACADEMYINFO_DB.school_list
UNION ALL
SELECT 'subject_list', COUNT(*), MAX(svy_yr), MAX(recv_time)
FROM ACADEMYINFO_DB.subject_list
UNION ALL
SELECT 'school_indicator_list', COUNT(*), MAX(indct_yr), MAX(recv_time)
FROM ACADEMYINFO_DB.school_indicator_list
UNION ALL
SELECT 'regional_indicator_list', COUNT(*), MAX(svy_yr), MAX(recv_time)
FROM ACADEMYINFO_DB.regional_indicator_list
UNION ALL
SELECT 'startup_support_list', COUNT(*), MAX(svy_yr), MAX(recv_time)
FROM ACADEMYINFO_DB.startup_support_list;
```

- `school_indicator_list` 는 최근 로그 파일명과 마지막 offset 범위를 같이 표기한다.
- `startup_support_list` 는 최신 년도와 최근 `recv_time` 둘 다 유지한다.

### 로그 경로 규칙

#### career

- 기준 경로: `/var/www/html/update/career/logs/`
- 상태 페이지 연결 대상:
  - `sync_school_list.log`
  - `sync_subject_list.log`
  - `sync_subject_detail.log`
  - `manual_sync_school_list.log`
  - `manual_sync_subject_list.log`
  - `manual_sync_aptitude_meta.log`

#### academyinfo

- 기준 경로: `/var/www/html/update/academyinfo/logs/`
- 상태 페이지 연결 대상:
  - `sync_school_indicator_batch.log`
  - `sync_school_indicator*.log`
  - `sync_startup_support.log`
  - `sync_school_list.log`
  - `sync_subject_list.log`

### `collector_runs.html` 판정 규칙

- 성공/실패는 별도 실행 이력 테이블을 새로 만들지 않고 **기존 로그 문자열 규칙**으로 1차 판정한다.
- 성공:
  - 마지막 의미 있는 줄에 `완료`, `총`, `동기화 완료`, `saved`, `commit` 중 하나가 있고
  - 같은 실행 구간 안에 `Traceback` 또는 `HTTP 429` 가 없다.
- 경고:
  - `HTTP 429` 문자열이 있으면 경고로 본다.
  - `sync-school-indicators batch offset=` 패턴이 있으면 마지막 offset/limit/count 를 같이 노출한다.
- 실패:
  - `Traceback`, `ERROR`, `failed` 문자열이 마지막 실행 구간에 있으면 실패로 본다.

### 책임 경계 재확인

- 여기서 확정하는 것은 `robocode-admin/db/` 가 읽을 **SQL/로그 계약**까지만이다.
- PHP 조회 구현, HTML 표 렌더링, 수동 새로고침 UX는 `robocode-admin` 책임이다.
- 수집기 로직 수정, cron 변경, DB 스키마 변경은 계속 `update` 책임이다.

## 8. 구현 순서 세분화

1. `update` 쪽에서 테이블별 최근시각/건수 조회 SQL 확정 (`UPDATE_MONITORING_DATA_CONTRACT.md`)
2. `academyinfo` 분할 로그 파일명 규칙 확정 (`UPDATE_MONITORING_DATA_CONTRACT.md`)
3. `robocode-admin/db/*.php` 에서 공통 조회 로직 작성
4. 외부 노출용 `.html` 은 표/링크만 두고 실제 데이터는 `.php` 가 담당
5. 운영 중 필요한 항목이 늘어나면 `update` 문서에서 먼저 데이터 계약을 확정하고 화면에 반영


## 8. 스펙/조회 페이지 구현 기준

- `specs.php`
  - 데이터 소스: `/var/www/html/update/academyinfo/SERVICE_SPEC_STATUS.md`, `/var/www/html/update/career/SERVICE_SPEC_STATUS.md`
  - 방식: `## 스펙별 상태` markdown 표를 읽어 관리자 표로 렌더링
  - 장점: 수집기 기준 문서와 관리자 표가 자동으로 맞춰짐
- `schools.php`
  - 데이터 소스: `ACADEMYINFO_DB.school_list`, `CAREER_DB.school_list`
  - 기본 기능: 도메인 필터, 학교명 검색, 최근 적재시각 확인
- `subjects.php`
  - 데이터 소스: `ACADEMYINFO_DB.subject_list`, `CAREER_DB.subject_list`
  - 기본 기능: 도메인 필터, 학과명 검색, 학교/단과대/계열 보조 정보 확인

## 9. nznlab / robocode-admin 연동 스모크 기준

서버 `/var/www/html` 기준 구현 후 최소 스모크는 아래 순서로 본다.

1. 문법 확인
   - `php -l /var/www/html/nznlab/db/career/status.inc`
   - `php -l /var/www/html/nznlab/db/academyinfo/status.inc`
   - `php -l /var/www/html/nznlab/db/career/schools.inc`
   - `php -l /var/www/html/nznlab/db/academyinfo/schools.inc`
   - `php -l /var/www/html/nznlab/db/career/subjects.inc`
   - `php -l /var/www/html/nznlab/db/academyinfo/subjects.inc`
   - `php -l /var/www/html/robocode-admin/db/career_status.php`
   - `php -l /var/www/html/robocode-admin/db/academyinfo_status.php`
   - `php -l /var/www/html/robocode-admin/db/schools.php`
   - `php -l /var/www/html/robocode-admin/db/subjects.php`
2. 조회 함수 단독 확인
   - `career_get_status_rows()` 는 `code_list`, `job_list`, `school_list`, `subject_list`, `subject_detail_list` 5행을 반환해야 한다.
   - `academyinfo_get_status_rows()` 는 `year_list`, `school_list`, `subject_list`, `school_indicator_list`, `regional_indicator_list`, `startup_support_list` 를 포함해야 한다.
   - `career_get_schools()`, `academyinfo_get_schools()` 는 빈 검색어 기준 최근 `recv_time desc` 정렬 1페이지 응답이 나와야 한다.
   - `career_get_subjects()`, `academyinfo_get_subjects()` 도 같은 방식으로 1페이지 응답을 확인한다.
3. 페이지 스모크 확인
   - `career_status.php`, `academyinfo_status.php` 는 빈 GET 기준 경고/치명 오류 없이 표 HTML 을 렌더해야 한다.
   - `schools.php?domain=career&q=` 와 `subjects.php?domain=academyinfo&q=` 는 최소 1건 이상 또는 빈 결과 표를 정상 렌더해야 한다.
   - `collector_runs.php` 는 `sync_school_indicator_batch.log` 의 마지막 batch offset 과 `HTTP 429` 문자열 노출 여부를 함께 보여줘야 한다.
4. 운영 확인 포인트
   - 상태 페이지의 비고 컬럼은 `UPDATE_MONITORING_DATA_CONTRACT.md` 의 작업명↔로그 파일 규칙과 동일해야 한다.
   - `school_indicator_list` 최신 연도 표시는 `MAX(indct_yr)` 기준으로 맞춘다.
   - `school_indicator_list` 는 행 수만 보여주고 끝내지 말고 최근 로그 판단 결과를 같이 붙인다.
   - 적성검사 API는 사용자 기능 본체가 아니라 운영 로그 관찰 대상으로만 다룬다.
