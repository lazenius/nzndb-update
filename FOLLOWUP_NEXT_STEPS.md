# 후속 작업 우선순위 및 검증 체크리스트

## 전제

- 이 저장소는 서버 `/var/www/html/update` 기준 코드/문서 스냅샷이다. 실행·cron·적재 검증의 최종 근거는 서버에서 다시 확인한다. (`AGENTS.md`, `career/IMPLEMENTATION_SCOPE.md`)
- `update` 는 수집/적재 책임만 가지며, 모니터링 화면은 `robocode-admin` 에서 분리 구현한다. (`UPDATE_ROBOCODE_ADMIN_SPLIT.md`)

## 바로 이어갈 작업 1 — academyinfo `school_indicator_list` 분할 cron 운영 확정

### 근거
- `IMPLEMENTATION_GAPS.md` 에서 현재 최우선 항목으로 지정돼 있다.
- `TODO.md` 의 다음 시작 지점도 같은 항목이다.
- `academyinfo/README.md` 는 서버 cron 등록 완료까지는 반영됐지만, 429 완화용 분할 운영 기준은 문서상 미완료다.

### 해야 할 일
1. 서버 `/var/www/html/update/academyinfo` 기준 현재 crontab 과 최근 로그에서 `sync_school_indicator*` 실행 단위 확인
2. `--school-offset`, `--school-limit` 분할값을 운영안으로 확정
3. 로그 파일명 규칙과 429 탐지 기준을 문서에 고정

### 완료 기준
- 분할 배치 단위와 실행 시각이 문서 1곳에 확정돼 있다.
- 최근 로그 1회 이상에서 offset 범위와 성공/429 여부를 재확인했다.

## 바로 이어갈 작업 2 — career 학교/학과 수집 cron 편입 여부와 최근 적재 로그 검증

### 근거
- `IMPLEMENTATION_GAPS.md` 에서 2순위다.
- `career/IMPLEMENTATION_SCOPE.md` 는 `sync-school-list`, `sync-subject-list` 의 서버 운영 확인이 남아 있다고 적고 있다.
- `UPDATE_ROBOCODE_ADMIN_SPLIT.md` 도 이 두 명령의 정기 실행 유무를 모니터링 핵심 항목으로 둔다.

### 해야 할 일
1. 서버 `/var/www/html/update/career` 기준 crontab 에 `sync-school-list`, `sync-subject-list` 등록 여부 확인
2. 최근 로그에서 적재 건수와 마지막 성공 시각 확인
3. 모니터링용 최소 SQL(`행 수`, `max(recv_time)`) 후보를 함께 문서화

### 완료 기준
- cron 등록 여부가 예/아니오로 명시돼 있다.
- `school_list`, `subject_list` 최신 적재 근거가 로그 또는 DB 조회로 남아 있다.

## 바로 이어갈 작업 3 — robocode-admin 1차 상태 페이지용 데이터 계약 확정

### 근거
- `TODO.md` 미완료 항목이다.
- `UPDATE_ROBOCODE_ADMIN_SPLIT.md` 에 필요한 페이지/테이블/표시 컬럼이 이미 정리돼 있다.
- 현재 `update` 쪽에서 먼저 확정해야 할 것은 UI가 아니라 조회 SQL/로그 경로 규칙이다.

### 해야 할 일
1. `career_status`, `academyinfo_status`, `collector_runs` 에 필요한 SQL과 로그 경로 규칙을 루트 문서로 고정
2. `HTTP 429` 를 문자열 검색으로 볼지, 별도 실행 이력 테이블이 필요한지 결정
3. 그 결과만 `robocode-admin/db/` 구현 입력 계약으로 넘김

### 완료 기준
- 페이지별 데이터 소스, 최소 컬럼, SQL 또는 로그 추출 규칙이 확정돼 있다.
- `update` 와 `robocode-admin` 책임 경계가 문서상 다시 섞이지 않는다.

## 지금 보류할 항목

- `career` 적성검사 API는 정기 적재보다 사용자 상호작용 성격이 강하므로 별도 웹 영역 우선 검토 유지 (`IMPLEMENTATION_GAPS.md`, `UPDATE_ROBOCODE_ADMIN_SPLIT.md`)
- `career/update_major_view.py` 기반 학과 상세 확장은 운영 우선순위 3개가 끝난 뒤 재평가
- `academyinfo` 산학협력 7개 API 정규화는 운영 안정화 이후로 미룬다

## 검증 체크리스트

### 문서/정책 검증
- [ ] `IMPLEMENTATION_GAPS.md` 우선순위와 새 결정이 충돌하지 않음
- [ ] `TODO.md` 미완료 항목과 새 작업 순서가 일치함
- [ ] `UPDATE_ROBOCODE_ADMIN_SPLIT.md` 책임 분리가 유지됨

### 서버 운영 검증
- [ ] 서버 crontab 에 academyinfo 분할 배치 등록 현황 확인
- [ ] 서버 crontab 에 career `sync-school-list`, `sync-subject-list` 등록 현황 확인
- [ ] 최근 로그에서 academyinfo 429 여부/offset 범위 확인
- [ ] 최근 로그에서 career 학교/학과 적재 성공 여부 확인

### 코드/테스트 검증
- [ ] `python3 -m unittest academyinfo.tests.test_update_academyinfo`
- [ ] `python3 -m unittest career.test_update_career`
- [ ] `python3 -m py_compile academyinfo/update_academyinfo.py career/update_career.py`

## 공유 파일 / 위험 메모

- 실제 cron, 로그, DB 적재 증거는 서버 기준이라 로컬 문서만으로 완료 처리하면 안 된다.
- `TODO.md`, `AGENTS.md` 는 팀 공용 문맥이 강하므로 이번 후속 정리 자체는 별도 문서로 유지하는 편이 안전하다.
- `robocode-admin` 구현 파일은 이 저장소 책임 밖이므로 여기서는 데이터 계약까지만 확정한다.
