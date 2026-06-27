# update 모니터링 데이터 계약

## 목적

- `robocode-admin/db/` 가 `update` DB와 로그를 **읽기 전용**으로 조회할 때 사용할 최소 계약을 고정한다.
- 이 문서는 UI 설계가 아니라 **조회 SQL / 로그 경로 / 판정 규칙**만 정의한다.
- 실제 실행/cron/로그의 최종 근거는 서버 `/var/www/html/update` 기준이다.

## 책임 경계

- `update`
  - 수집기 실행
  - DB 적재
  - cron 운영
  - 로그 파일 생성
  - 조회 가능한 최소 SQL / 로그 규칙 유지
- `robocode-admin`
  - 읽기 전용 PHP 조회
  - 상태 표 렌더링
  - 최근 로그 요약 표시

## 1. `career_status.html` 데이터 계약

### 대상 DB

- 스키마: `CAREER_DB`
- 최소 표:
  - `code_list`
  - `job_list`
  - `school_list`
  - `subject_list`
  - `subject_detail_list`

### 공통 SQL 패턴

```sql
SELECT COUNT(*) AS row_count,
       MAX(recv_time) AS last_recv_time
FROM CAREER_DB.{table_name};
```

### 권장 조회 목록

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
FROM CAREER_DB.subject_list
UNION ALL
SELECT 'subject_detail_list', COUNT(*), MAX(recv_time)
FROM CAREER_DB.subject_detail_list;
```

### 보조 비고 규칙

- `code_list` → `sync-code-list`
- `job_list` → `sync-job-list`
- `school_list` → `sync-school-list`
- `subject_list` → `sync-subject-list`
- `subject_detail_list` → `sync-subject-detail`
- 비고 컬럼에는 cron 등록 여부와 대응 로그 파일명을 함께 표기한다.

### 대응 로그 파일

- `/var/www/html/update/career/logs/sync_code_list.log`
- `/var/www/html/update/career/logs/sync_job_list.log`
- `/var/www/html/update/career/logs/sync_school_list.log`
- `/var/www/html/update/career/logs/sync_subject_list.log`
- `/var/www/html/update/career/logs/sync_subject_detail.log`
- `/var/www/html/update/career/logs/sync_aptitude_meta.log`

## 2. `academyinfo_status.html` 데이터 계약

### 대상 DB

- 스키마: `ACADEMYINFO_DB`
- 최소 표:
  - `code_list`
  - `year_list`
  - `school_list`
  - `subject_list`
  - `school_indicator_list`
  - `regional_indicator_list`
  - `startup_support_list`

### 공통 SQL 패턴

```sql
SELECT COUNT(*) AS row_count,
       MAX(recv_time) AS last_recv_time
FROM ACADEMYINFO_DB.{table_name};
```

### 권장 조회 목록

```sql
SELECT 'code_list' AS table_name, COUNT(*) AS row_count, MAX(recv_time) AS last_recv_time
FROM ACADEMYINFO_DB.code_list
UNION ALL
SELECT 'year_list', COUNT(*), MAX(recv_time)
FROM ACADEMYINFO_DB.year_list
UNION ALL
SELECT 'school_list', COUNT(*), MAX(recv_time)
FROM ACADEMYINFO_DB.school_list
UNION ALL
SELECT 'subject_list', COUNT(*), MAX(recv_time)
FROM ACADEMYINFO_DB.subject_list
UNION ALL
SELECT 'school_indicator_list', COUNT(*), MAX(recv_time)
FROM ACADEMYINFO_DB.school_indicator_list
UNION ALL
SELECT 'regional_indicator_list', COUNT(*), MAX(recv_time)
FROM ACADEMYINFO_DB.regional_indicator_list
UNION ALL
SELECT 'startup_support_list', COUNT(*), MAX(recv_time)
FROM ACADEMYINFO_DB.startup_support_list;
```

### 추가 조회

최신 기준 연도/조사연도를 같이 보여주려면 아래 보조 조회를 사용한다.

```sql
SELECT MAX(year_val) AS latest_year
FROM ACADEMYINFO_DB.year_list;

SELECT MAX(svy_yr) AS latest_school_year
FROM ACADEMYINFO_DB.school_list;

SELECT MAX(indct_yr) AS latest_indicator_year
FROM ACADEMYINFO_DB.school_indicator_list;
```

### 대응 로그 파일

- `/var/www/html/update/academyinfo/logs/sync_code_year.log`
- `/var/www/html/update/academyinfo/logs/sync_school_master.log`
- `/var/www/html/update/academyinfo/logs/sync_subject_master.log`
- `/var/www/html/update/academyinfo/logs/sync_school_indicator_batch.log`
- `/var/www/html/update/academyinfo/logs/sync_regional_indicator.log`
- `/var/www/html/update/academyinfo/logs/sync_startup_support.log`

### `school_indicator_list` 비고 규칙

- 최근 `recv_time` 외에 아래를 함께 본다.
  - 마지막 batch offset/limit
  - 마지막 `HTTP 429` 발생 여부
  - 마지막 실패 endpoint 1줄
- `school_indicator_list` 상태는 DB 행 수만으로 끝내지 않고 `sync_school_indicator_batch.log` 와 함께 판정한다.

## 3. `collector_runs.html` 데이터 계약

### 대상 로그 루트

- `/var/www/html/update/career/logs/`
- `/var/www/html/update/academyinfo/logs/`

### 최소 표시 컬럼

- 작업명
- 로그 파일명
- 마지막 실행시각
- 성공/실패 추정
- 마지막 의미 있는 로그 1줄
- 비고

### 작업명 ↔ 로그 파일 매핑

| 작업명 | 로그 파일 |
|---|---|
| `career sync-code-list` | `career/logs/sync_code_list.log` |
| `career sync-job-list` | `career/logs/sync_job_list.log` |
| `career sync-school-list` | `career/logs/sync_school_list.log` |
| `career sync-subject-list` | `career/logs/sync_subject_list.log` |
| `career sync-subject-detail` | `career/logs/sync_subject_detail.log` |
| `career sync-aptitude-meta` | `career/logs/sync_aptitude_meta.log` |
| `academyinfo sync-code-year` | `academyinfo/logs/sync_code_year.log` |
| `academyinfo sync-school-master` | `academyinfo/logs/sync_school_master.log` |
| `academyinfo sync-subject-master` | `academyinfo/logs/sync_subject_master.log` |
| `academyinfo sync-school-indicators` | `academyinfo/logs/sync_school_indicator_batch.log` |
| `academyinfo sync-regional-indicators` | `academyinfo/logs/sync_regional_indicator.log` |
| `academyinfo sync-startup-support` | `academyinfo/logs/sync_startup_support.log` |

### 성공/실패 추정 규칙

- `HTTP 429` 문자열 포함 → 실패
- `Traceback` 문자열 포함 → 실패
- `ERROR` 문자열 포함 → 실패
- `현재 배치까지 반영 후 중단` 문자열 포함 → 실패(부분반영)
- 위 실패 문자열이 없고, 마지막 의미 있는 줄이 총건수/완료 성격이면 성공 추정

### `academyinfo sync-school-indicators` 추가 규칙

- `[batch] offset=<n> limit=<m>` 헤더를 마지막 batch 범위의 기준으로 본다.
- 마지막 `HTTP 429` 줄이 있으면 비고에 endpoint 와 `schl_id/svy_yr` 일부를 함께 보여준다.
- 성공 추정이라도 마지막 batch 헤더가 있고 종료 요약이 없으면 `확인 필요` 로 표기 가능하다.

## 4. cron 등록 비고 기준

상태 페이지의 비고 컬럼에는 아래처럼 고정 문자열을 써도 된다.

- `cron 등록됨 / 로그 확인 필요`
- `cron 등록됨 / 최근 성공 확인`
- `cron 등록됨 / 429 재확인 필요`
- `수동 실행만 확인`

## 5. 운영 메모

- `career` 학교/학과는 문서상 정기 cron 반영 상태를 기준으로 본다.
- `academyinfo school_indicator_list` 는 cron 등록은 됐지만, 2026-06-27 기준 `HTTP 429` 완화 운영은 아직 닫지 않았다.
- 따라서 `collector_runs.html` 에서는 `academyinfo sync-school-indicators` 를 일반 성공 로그보다 우선 감시 대상으로 둔다.
