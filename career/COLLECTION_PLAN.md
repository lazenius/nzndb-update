# Career 수집 주기 / cron 계획

## 기준

- 기준 문서:
  - `career/DB_SCHEMA.md`
  - `career/IMPLEMENTATION_SCOPE.md`
  - `career/OpenAPIExample/jobdiclist.html`
  - `career/OpenAPIExample/jobdicview.html`
- 로컬 문서 기준 스펙 수: **5**
- 로컬 문서 기준 테이블 수: **23**
- 현재 상태:
  - 로컬에 `career/update_career.py` 초안 수집기 있음
  - 서버 cron 등록 없음
  - 따라서 이 문서는 **초안 수집기 + 권장 운영 계획** 기준이다.

## 스펙별 주기 산정

### 1) 월 1회 코드표 동기화 — 3개

- 대상:
  - `themes.json`
  - `aptds.json`
  - `jobcodes.json`
- 이유:
  - 코드성 마스터 데이터라 변동 빈도가 낮다.
  - 일/주 단위 재수집 이득이 작다.
- 적재 대상:
  - `code_list`

### 2) 주 1회 목록 동기화 — 1개 + 확장 예정 2개

- 현재 문서 기준 대상:
  - `jobs.json`
- 2차 확장 예정:
  - 학교 목록 API
  - 학과 목록 API
- 이유:
  - 목록성 데이터는 신규/수정 반영 필요가 있다.
  - 하지만 일배치까지는 과하고 주간 동기화가 현실적이다.
- 적재 대상:
  - `job_list`
  - 확장 시 `school_list`, `subject_list`

### 3) 월 1회 상세 전체 재동기화 — 1개 + 확장 예정 1개

- 현재 문서 기준 대상:
  - `job.json`
- 2차 확장 예정:
  - 학과 상세 API
- 이유:
  - 상세 API는 호출량이 크다.
  - 목록에서 식별자 키를 먼저 확보하고, 상세는 후행 배치가 효율적이다.
  - 차트/반복 노드까지 포함하면 월 단위 전체 재동기화가 운영상 단순하다.
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
  - 확장 시 `subject_detail_list`, `subject_text_list`, `subject_school_map`, `subject_chart_list`, `subject_feature_list`

## 권장 운영 배치

### 배치 A — 매월 1일 02:10

코드표 동기화

- `themes.json`
- `aptds.json`
- `jobcodes.json`

### 배치 B — 매주 월요일 02:20

직업 목록 동기화

- `jobs.json`

### 배치 C — 매월 3일 02:30

직업 상세 전체 재수집

- `job.json`

### 배치 D — 2차 확장 후 매주 월요일 03:00

학교 목록 동기화

- 학교 목록 API

### 배치 E — 2차 확장 후 매주 월요일 03:30

학과 목록 동기화

- 학과 목록 API

### 배치 F — 2차 확장 후 매월 4일 02:30

학과 상세 전체 재수집

- 학과 상세 API

## 권장 cron 초안

아직 수집기가 없으므로 **실등록용 cron이 아니라 계획용 초안**이다.

```cron
10 2 1 * * cd /var/www/html/update/career && /usr/bin/python3 update_career.py sync-code-list >> logs/sync_code_list.log 2>&1
20 2 * * 1 cd /var/www/html/update/career && /usr/bin/python3 update_career.py sync-job-list >> logs/sync_job_list.log 2>&1
30 2 3 * * cd /var/www/html/update/career && /usr/bin/python3 update_career.py sync-job-detail >> logs/sync_job_detail.log 2>&1
0 3 * * 1 cd /var/www/html/update/career && /usr/bin/python3 update_career.py sync-school-list >> logs/sync_school_list.log 2>&1
30 3 * * 1 cd /var/www/html/update/career && /usr/bin/python3 update_career.py sync-subject-list >> logs/sync_subject_list.log 2>&1
30 2 4 * * cd /var/www/html/update/career && /usr/bin/python3 update_career.py sync-subject-detail >> logs/sync_subject_detail.log 2>&1
```

## 구현 순서 권장

1. `code_list` 수집기 구현
2. `job_list` 수집기 구현
3. `job.json` 상세 적재기 구현
4. 학교/학과 목록 API 실응답 확보
5. `school_list`, `subject_list` 수집기 구현
6. 학과 상세 적재기 구현
7. 서버 배포 후 cron 실등록

## 검증 포인트

- `jobs.json` 목록에서 상세 수집 대상 키를 안정적으로 확보할 수 있어야 한다.
- `job.json` 반복 노드는 직업코드 기준 삭제 후 재적재 방식이 단순하다.
- `edu_chart`, `major_chart`, `indicator_chart`는 현재 PK가 단순해 실응답 기준 재검토가 필요하다.
- 학교/학과 API는 아직 문서 기준만 있으므로, 주기 확정 전 실응답 샘플 재검증이 필요하다.

## 현재 반영 상태

- 문서 작성 완료
- 수집기 초안 작성 완료 (`career/update_career.py`)
- 서버 cron 미등록
- 실제 운영 배치 미시작
