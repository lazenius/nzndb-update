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
- `/var/www/html/update/academyinfo/logs/sync_school_indicator.log`
- `/var/www/html/update/academyinfo/logs/sync_regional_indicator.log`
- `/var/www/html/update/academyinfo/logs/sync_startup_support.log`

등록 cron:

```cron
10 2 1 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-code-year --scope latest >> logs/sync_code_year.log 2>&1
20 2 * * 1 cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-master --scope latest >> logs/sync_school_master.log 2>&1
40 2 * * 1 cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-subject-master --scope latest >> logs/sync_subject_master.log 2>&1
10 3 3 * * cd /var/www/html/update/academyinfo && /usr/bin/python3 update_academyinfo.py sync-school-indicators --scope latest >> logs/sync_school_indicator.log 2>&1
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

## 구현 한계

- `getCodeBySeriesSystem`은 현재 테이블 구조상 완전 정규화보다 raw 저장이 안전하다.
- `getSchoolMajorInfo`는 `schl_mjr_id`가 직접 오지 않아 `getUniversityMajorCode` 결과와 **보강 merge** 방식으로 처리한다.
- 산학협력 7개 API는 현재 `startup_support_list`에 key-value 형태로 우선 적재한다.
