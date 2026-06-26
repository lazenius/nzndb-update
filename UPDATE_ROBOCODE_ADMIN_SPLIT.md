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

### 최소 1차 화면

| 페이지 | 목적 |
|---|---|
| `career_status.html` | career 수집 테이블별 건수/최근 갱신시각 확인 |
| `academyinfo_status.html` | academyinfo 수집 테이블별 건수/최근 갱신시각 확인 |
| `collector_runs.html` | 최근 실행 로그/성공실패 확인 |

### 1차 데이터 소스 정의

| 페이지 | 주 조회 대상 | 최소 확인 항목 |
|---|---|---|
| `career_status.html` | `code_list`, `job_list`, `school_list`, `subject_list` | 테이블별 건수, 최근 `recv_time`, 마지막 성공 로그 파일명 |
| `academyinfo_status.html` | `year_list`, `school_list`, `subject_list`, `school_indicator_list`, `regional_indicator_list`, `startup_support_list` | 테이블별 건수, 최신 년도, 최근 `recv_time`, 최근 배치 로그 |
| `collector_runs.html` | `update` 각 수집기 로그 파일 | 작업명, 시작시각, 종료시각, 성공/실패, 429 여부 |

### 1차 후속 정의

- `update` 쪽에서 제공해야 할 기준
  - 테이블별 최근 적재시각을 뽑을 수 있는 SQL
  - 수집기별 로그 파일 경로 규칙
  - `HTTP 429` 같은 운영 경고를 문자열 검색으로 잡을지, 별도 실행 이력 테이블로 뽑을지 결정
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

## 7. 구현 순서 세분화

1. `update` 쪽에서 테이블별 최근시각/건수 조회 SQL 확정
2. `academyinfo` 분할 로그 파일명 규칙 확정
3. `robocode-admin/db/*.php` 에서 공통 조회 로직 작성
4. 외부 노출용 `.html` 은 표/링크만 두고 실제 데이터는 `.php` 가 담당
5. 운영 중 필요한 항목이 늘어나면 `update` 문서에서 먼저 데이터 계약을 확정하고 화면에 반영
