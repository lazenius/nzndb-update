# Academyinfo 수집 주기 / cron 계획

## 기준

- 기준 스펙 문서: `academyinfo/API_SPEC.md`
- 총 스펙 수: **103**
- 수집기: `academyinfo/update_academyinfo.py`
- 기본 정책:
  - **코드/년도성 메타데이터**는 월 1회
  - **학교/학과 마스터**는 주 1회
  - **지표/통계/산학협력**은 월 1회
  - cron 기본 범위는 `--scope latest`
  - 단, 학교/학과 마스터는 `latest` 실행 시 **빈 최신연도면 최근 유효연도로 fallback**

## 주기 산정 결과

### 1) 월 1회 메타데이터 갱신 — 19개

- 대상:
  - `getCodeByRegion`
  - `getKeyIndicatorCode`
  - `getComparisonPubYear`
  - `getCodeByFound`
  - `getNoticeSvyYear`
  - `getCodeByType`
  - `getCodeByKind`
  - `getCodeByLargeSeries`
  - `getCodeByMiddleSeries`
  - `getCodeBySeriesSystem`
  - `getCodeByPrincipalSchoolBranchSchool`
  - `getCodeByLessonTerm`
  - `getCodeByDegreeCourse`
  - `getCodeByDayAndNight`
  - `getCodeByCollege`
  - `getCodeByMajorStatus`
  - `getCodeByMajorCharacter`
  - `getCodeByOneselfSeries`
  - `getCodeBySmallSeries`
- 이유:
  - 코드/년도는 실시간 변동 데이터가 아니다.
  - 새 조사년도/공시년도, 코드 체계 변경 감지만 되면 충분하다.
- 적재:
  - `code_list`
  - `year_list`
  - `getCodeBySeriesSystem`은 현재 **raw 보관 우선**

### 2) 주 1회 학교/학과 마스터 갱신 — 6개

- 대상:
  - `getUniversityCode`
  - `getNoticeUniversitySearchList`
  - `getComparisonUniversitySearchList`
  - `getUniversityMajorCode`
  - `getSchoolMajorInfo`
  - `getSchoolInfo`
- 이유:
  - 학교 기본정보/학과 기본정보는 일간 변화보다 주간 재동기화가 현실적이다.
  - `getUniversityCode` + `getSchoolInfo` merge, `getUniversityMajorCode` + `getSchoolMajorInfo` merge 구조라 메타보다 자주 보는 편이 안전하다.
- 적재:
  - `school_list`
  - `subject_list`

### 3) 월 1회 지표/통계/산학협력 갱신 — 78개

- 대상:
  - 교육여건 12개
  - 교원·연구 22개
  - 학생 27개
  - 재정 10개
  - 산학협력 7개
- 이유:
  - 대학알리미/대학정보공시 성격상 월간 또는 공시 시점 반영이 적합하다.
  - 학교별/지역별 지표는 대량 호출이라 주 1회보다 월 1회가 운영비용 대비 현실적이다.
- 적재:
  - `school_indicator_list`
  - `regional_indicator_list`
  - `startup_support_list`

## cron 등록 계획

서버 기준 경로:

- 프로젝트 루트: `/var/www/html/update`
- academyinfo 루트: `/var/www/html/update/academyinfo`

로그 파일:

- `/var/www/html/update/academyinfo/logs/sync_code_year.log`
- `/var/www/html/update/academyinfo/logs/sync_school_master.log`
- `/var/www/html/update/academyinfo/logs/sync_subject_master.log`
- `/var/www/html/update/academyinfo/logs/sync_school_indicator_a.log`
- `/var/www/html/update/academyinfo/logs/sync_school_indicator_b.log`
- `/var/www/html/update/academyinfo/logs/sync_school_indicator_c.log`
- `/var/www/html/update/academyinfo/logs/sync_school_indicator_d.log`
- `/var/www/html/update/academyinfo/logs/sync_regional_indicator.log`
- `/var/www/html/update/academyinfo/logs/sync_startup_support.log`

등록 cron:

```cron
10 2 1 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-code-year --scope latest >> logs/sync_code_year.log 2>&1
20 2 * * 1 cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-master --scope latest >> logs/sync_school_master.log 2>&1
40 2 * * 1 cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-subject-master --scope latest >> logs/sync_subject_master.log 2>&1
10 3 3 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-indicators --scope latest --school-offset 0 --school-limit 100 >> logs/sync_school_indicator_a.log 2>&1
40 3 3 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-indicators --scope latest --school-offset 100 --school-limit 100 >> logs/sync_school_indicator_b.log 2>&1
10 4 3 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-indicators --scope latest --school-offset 200 --school-limit 100 >> logs/sync_school_indicator_c.log 2>&1
40 4 3 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-indicators --scope latest --school-offset 300 --school-limit 100 >> logs/sync_school_indicator_d.log 2>&1
10 4 4 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-regional-indicators --scope latest >> logs/sync_regional_indicator.log 2>&1
10 5 5 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-startup-support --scope latest >> logs/sync_startup_support.log 2>&1
```

## 현재 반영 상태

- 서버 git 저장소 초기화 완료
- GitHub 원격 연결 완료: `git@github.com:lazenius/nzndb-update.git`
- cron 등록 완료
- 수동 검증 완료:
  - `sync-code-year --scope latest`
  - `sync-school-master --scope latest` → 2026 빈 응답 확인 후 2025 fallback 동작 반영
  - `sync-school-indicators --scope latest --school-offset 0 --school-limit 1` → 2026-06-27 스모크 통과

## `HTTP 429` 운영 안정화안

### 현재 코드 기준

- 공통 호출부 `academyinfo/include/common.py` 는 `429/502/503/504`에 대해 `0 → 2 → 5 → 15 → 30초` 재시도를 수행한다.
- `sync-school-indicators` 는 재시도 후에도 `429`가 나면 **현재 배치까지 commit 후 중단**한다.
- `sync-regional-indicators` 는 공통 재시도만 있고, `sync-school-indicators` 같은 중간 commit/중단 처리 분기는 없다.
- `sync-subject-master`, `sync-school-indicators` 는 `--school-offset`, `--school-limit` 배치 실행이 가능하다.
- `sync-startup-support` 도 `--school-offset`, `--school-limit` 배치 실행이 가능하다.

### 운영 권장안

1. `sync-school-indicators` 를 단일 월배치 1회 대신 **학교 범위 분할 cron** 으로 운영한다.
2. 실패 시 전체 재실행보다 **마지막 미완료 offset부터 재실행**한다.
3. `sync-regional-indicators` 와 `sync-startup-support` 는 다른 날/시간대로 유지해 동시 호출량을 줄인다.
4. `collector_runs.html` 에서는 `sync_school_indicator_[a-d].log` 의 마지막 성공 offset/실패 시각을 바로 보이게 한다.
5. 2026-06-27 서버 최신 `school_list` 기준 학교 수는 `377`건이므로, 운영 배치는 `100`건 단위 4분할을 기본값으로 둔다.

### 분할 cron 예시

```cron
10 3 3 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-indicators --scope latest --school-offset 0 --school-limit 100 >> logs/sync_school_indicator_a.log 2>&1
40 3 3 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-indicators --scope latest --school-offset 100 --school-limit 100 >> logs/sync_school_indicator_b.log 2>&1
10 4 3 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-indicators --scope latest --school-offset 200 --school-limit 100 >> logs/sync_school_indicator_c.log 2>&1
40 4 3 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-indicators --scope latest --school-offset 300 --school-limit 100 >> logs/sync_school_indicator_d.log 2>&1
```

### 검증 포인트

- 분할 실행 후 `school_indicator_list` 건수가 배치 간 누락 없이 누적되는지 확인
- `429` 발생 시 로그에 **어느 endpoint / 어느 school offset 범위**에서 멈췄는지 남는지 확인
- 다음 달 실행에서도 같은 offset 크기가 유지 가능한지 확인
- `sync-startup-support` 도 동일 문제가 반복되면 학교 배치 옵션 추가를 후속 과제로 승격

## 구현 한계

- `getCodeBySeriesSystem`은 현재 테이블 구조상 완전 정규화보다 raw 저장이 안전하다.
- `getSchoolMajorInfo`는 `schl_mjr_id`가 직접 오지 않아 `getUniversityMajorCode` 결과와 **보강 merge** 방식으로 처리한다.
- 산학협력 7개 API는 현재 `startup_support_list`에 key-value 형태로 우선 적재한다.
