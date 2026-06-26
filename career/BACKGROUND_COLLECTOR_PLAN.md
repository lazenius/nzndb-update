# 백그라운드 수집기 개선 후보와 검증 계획

## 범위
- 대상 스크립트: `update_jobs.py`, `update_school.py`, `update_major.py`, `update_code.py`, `update_major_view.py`
- 목적: 현재 복원된 수집 스크립트를 운영 가능한 백그라운드 수집기로 올리기 위한 개선 우선순위와 검증 순서를 정리한다.

## 현재 구조 요약
- `update/career/update_jobs.py:34-87`는 페이지 루프 안에서 목록 조회 후 상세 조회를 다시 호출하고, 각 직업마다 문자열 SQL 3건을 즉시 실행한다.
- `update/career/update_school.py:44-90`와 `update/career/update_major.py:16-60`는 전체 XML을 한 번에 읽어 단일 트랜잭션으로 적재한다.
- `update/career/update_code.py:23-34`는 코드 마스터를 일괄 적재한다.
- `update/career/update_major_view.py:26-30`는 `print(soup.prettify())` 후 `exit()` 하는 탐색용 스크립트 상태다.
- `update/career/update_school_test.py:45-50`도 실질 테스트가 아니라 응답 덤프용 확인 스크립트다.

## 개선 후보

### 1. 실행 진입점 통합 + 파라미터화
우선순위: 높음

근거:
- 각 스크립트가 import 시점에 바로 실행되는 배치 스크립트 형태다.
- `gubun`, `subject`, 페이지 범위, dry-run 여부가 하드코딩되어 있어 재실행/부분 실행이 어렵다.

대상:
- `update/career/update_jobs.py:29-85`
- `update/career/update_school.py:6-18`
- `update/career/update_major.py:6-18`
- `update/career/update_major_view.py:18-30`

개선 방향:
- `main()` 진입점으로 감싸고 CLI 인자(`--service`, `--gubun`, `--page-start`, `--page-end`, `--dry-run`)를 받도록 정리
- 크론/백그라운드 실행은 단일 엔트리포인트에서 서비스별 분기

### 2. 체크포인트/배치 커밋 추가
우선순위: 높음

근거:
- `update_jobs.py`는 전체 루프가 끝날 때까지 `con.commit()`을 미룬다 (`update/career/update_jobs.py:34-87`).
- 중간 실패 시 진행 위치를 잃고 처음부터 다시 수집할 가능성이 크다.
- 학교/학과 수집도 전체 응답을 한 번에 적재한다 (`update/career/update_school.py:46-90`, `update/career/update_major.py:18-60`).

개선 방향:
- 페이지 단위 commit
- 마지막 성공 페이지/시퀀스 저장용 run_state 테이블 또는 파일 체크포인트 추가
- `--resume` 지원

### 3. 문자열 SQL 제거 + 파라미터 바인딩
우선순위: 높음

근거:
- 현재 SQL이 전부 f-string 조합이라 따옴표/특수문자 데이터에서 깨질 수 있다.
- 관련 구간:
  - `update/career/update_jobs.py:69-81`
  - `update/career/update_school.py:84-87`
  - `update/career/update_major.py:56-59`
  - `update/career/update_code.py:27-31`

개선 방향:
- `cur.execute(sql, params)` 또는 `executemany()`로 전환
- 텍스트 정규화 함수는 별도 helper로 한정

### 4. 수집 통계/실패 로그 표준화
우선순위: 중간

근거:
- 현재는 `print()`만 있고 성공/실패 건수, 소요 시간, 마지막 page/jcode 기록이 없다.
- `update_major_view.py`와 `update_school_test.py`는 디버그 출력이 그대로 남아 있다.

개선 방향:
- 서비스별 공통 로그 포맷: start/end, fetched, inserted, updated, skipped, failed
- 실패 상세는 재처리 가능한 식별자(`page`, `job_cd`, `seq`)와 함께 남김
- 디버그 스크립트는 `debug/` 성격으로 분리하거나 정식 수집기로 승격

### 5. API 호출량 절감과 단계 분리
우선순위: 중간

근거:
- `update_jobs.py`는 목록 1회 + 상세 N회 구조라 가장 비싸다 (`update/career/update_jobs.py:35-46`).
- 목록/상세/부가 테이블 적재가 한 파일에 섞여 있어 장애 지점이 넓다.

개선 방향:
- 1차: 목록/기본정보 수집
- 2차: 상세/부가 테이블 수집
- 필요 시 변경 감지(`edit_dt`) 기반 상세 재수집

### 6. 검증 가능한 테스트 표면 만들기
우선순위: 중간

근거:
- 현재 저장소에는 pytest/unittest 기반 자동 테스트가 없다.
- `update_school_test.py`는 이름만 test이고 실제 assertion이 없다.

개선 방향:
- API 응답 fixture(JSON/XML) 저장
- 파싱 함수와 DB 적재 함수를 분리
- fixture 기반 단위 테스트 + dry-run 스모크 테스트 추가

## 권장 실행 순서
1. 실행 진입점 통합 + 파라미터화
2. 문자열 SQL 제거
3. 체크포인트/배치 커밋 추가
4. 공통 로그/실패 기록 추가
5. 잡 목록/상세 수집 분리
6. fixture 기반 테스트 추가

## 검증 계획

### A. 정적 검증
- 목표: 리팩터링 후 스크립트가 최소한 문법적으로 안전한지 확인
- 명령 예시:
  - `python3 -m py_compile update/career/*.py`
  - 가능하면 `ruff check update/career`

### B. 파서 단위 검증
- 목표: XML/JSON fixture에서 필드 추출이 기존 스키마와 동일한지 확인
- 체크:
  - 학교: `school, seq, name, sch1, sch2, region, est`
  - 학과: `school, seq, name, faculty, others`
  - 직업: `code, std_code, emp_code, apt_code, wage`
- 방식:
  - fixture 입력 → dict 출력 비교
  - edge case: 빈 문자열, 특수문자, 숫자 포맷(`wage`), 신규 코드값

### C. SQL 적재 검증
- 목표: 파라미터 바인딩 전환 후 동일 키 기준 upsert가 유지되는지 확인
- 방식:
  - 테스트 DB 또는 임시 스키마에 2회 연속 실행
  - row count 증가 없이 `recv_time`만 갱신되는지 확인
  - 특수문자 포함 데이터(`'`, `,`, 괄호) 샘플 추가

### D. 체크포인트/재개 검증
- 목표: 중간 실패 후 이어받기가 되는지 확인
- 방식:
  - 의도적으로 page N에서 예외 발생
  - 재실행 시 N+1 또는 마지막 성공 지점부터 재개되는지 확인
  - 중복 적재 여부 확인

### E. 운영 스모크 검증
- 목표: 실제 API/DB 연결 상태에서 백그라운드 실행 가능성 확인
- 방식:
  - `--page-end 1` 또는 소량 샘플 옵션으로 실행
  - 로그에 start/end, fetched/inserted/failed count가 모두 남는지 확인
  - 대상 테이블 `recv_time` 갱신 확인

## 즉시 확인된 리스크
- `include.common`이 저장소에 없어 로컬 단독 실행 재현성이 낮다.
- `update_major_view.py`는 현재 운영 스크립트로 쓰기 어렵다 (`print` 후 `exit()`).
- 테스트 명령이 정식으로 정의되어 있지 않아, 다음 구현 단계에서 fixture/test harness를 먼저 깔아야 한다.
