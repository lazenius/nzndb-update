# Task 3 Worker 3 Summary

## 범위
- 코드 기준: `academyinfo/update_academyinfo.py`, `career/update_career.py`
- 문서 대조: `academyinfo/API_SPEC.md`, `academyinfo/COLLECTION_PLAN.md`, `academyinfo/SERVICE_SPEC_STATUS.md`, `career/COLLECTION_PLAN.md`, `career/SERVICE_SPEC_STATUS.md`, `career/IMPLEMENTATION_SCOPE.md`, `career/APTITUDE_API_SPEC.md`

## academyinfo 실제 command surface
- CLI 명령: `plan`, `sync-code-year`, `sync-school-master`, `sync-subject-master`, `sync-school-indicators`, `sync-regional-indicators`, `sync-startup-support`, `sync-all` (`academyinfo/update_academyinfo.py:1371-1405`)
- 공통 옵션:
  - `--scope latest|all` (`academyinfo/update_academyinfo.py:1387-1391`)
  - `--school-offset`, `--school-limit` (`academyinfo/update_academyinfo.py:1393-1403`)
- 실행 매핑:
  - `sync-code-year` → metadata 19개 (`academyinfo/update_academyinfo.py:1018-1043`, `1309-1310`)
  - `sync-school-master` → school master 4개 (`academyinfo/update_academyinfo.py:1046-1170`, `1311-1312`)
  - `sync-subject-master` → subject master 2개 (`academyinfo/update_academyinfo.py:1173-1197`, `1313-1320`)
  - `sync-school-indicators` → school indicator 38개 (`academyinfo/update_academyinfo.py:1200-1237`, `1321-1328`)
  - `sync-regional-indicators` → regional 33개 (`academyinfo/update_academyinfo.py:1240-1261`, `1329-1330`)
  - `sync-startup-support` → startup 7개 (`academyinfo/update_academyinfo.py:1264-1280`, `1331-1338`)
  - `sync-all` → 위 6개 작업 일괄 실행 (`academyinfo/update_academyinfo.py:1339-1363`)

## academyinfo 실제 endpoint/spec checklist
- 스펙 파싱은 `API_SPEC.md`를 직접 읽어 `host + /get... path + required_params`를 추출한다 (`academyinfo/update_academyinfo.py:225-284`)
- 분류 기준: metadata / school_master / subject_master / school_indicator / regional / startup (`academyinfo/update_academyinfo.py:291-341`)
- 코드 기준 총 스펙: 103개, 분류는 `19 + 4 + 2 + 38 + 33 + 7` (`python3 academyinfo/update_academyinfo.py plan`)

### academyinfo metadata 19
- host `apis.data.go.kr/B340014/BasicInformationService_2`
  - `/getCodeByRegion`, `/getKeyIndicatorCode`, `/getComparisonPubYear`, `/getCodeByFound`, `/getNoticeSvyYear`, `/getCodeByType`, `/getCodeByKind`
- host `apis.data.go.kr/B340014/BasicInformationService_1`
  - `/getCodeByLargeSeries`, `/getCodeByMiddleSeries`, `/getCodeBySeriesSystem`, `/getCodeByPrincipalSchoolBranchSchool`, `/getCodeByLessonTerm`, `/getCodeByDegreeCourse`, `/getCodeByDayAndNight`, `/getCodeByCollege`, `/getCodeByMajorStatus`, `/getCodeByMajorCharacter`, `/getCodeByOneselfSeries`, `/getCodeBySmallSeries`
- required param 패턴:
  - 기본 `serviceKey`
  - 연도형 일부는 `serviceKey + svyYr` (`academyinfo/update_academyinfo.py:1030-1043`)

### academyinfo school master 4
- `apis.data.go.kr/B340014/BasicInformationService_2/getUniversityCode` → `serviceKey, svyYr`
- `apis.data.go.kr/B340014/BasicInformationService_2/getNoticeUniversitySearchList` → `serviceKey, svyYr`
- `apis.data.go.kr/B340014/BasicInformationService_2/getComparisonUniversitySearchList` → `serviceKey, svyYr`
- `apis.data.go.kr/B340014/SchoolInfoService/getSchoolInfo` → `serviceKey, svyYr, schlKrnNm`
- 코드 호출 파라미터는 `svyYr`, `schlId`, `schlKrnNm` 조합 (`academyinfo/update_academyinfo.py:1063-1170`)

### academyinfo subject master 2
- `apis.data.go.kr/B340014/BasicInformationService_1/getUniversityMajorCode` → `serviceKey, svyYr, schlId`
- `apis.data.go.kr/B340014/SchoolMajorInfoService/getSchoolMajorInfo` → `serviceKey, svyYr, schlKrnNm`
- 코드 호출 파라미터는 `serviceKey, svyYr, schlId` + 필요시 `schlKrnNm` (`academyinfo/update_academyinfo.py:1179-1188`)

### academyinfo school indicator 38 / regional 33 / startup 7
- school indicator는 기본 `serviceKey, svyYr, schlId`, 일부만 `indctId` 추가 (`academyinfo/update_academyinfo.py:1215-1223`)
- regional은 기본 `serviceKey, schlDivCd`, 일부만 `indctId` 추가 (`academyinfo/update_academyinfo.py:1246-1258`)
- startup은 현재 전부 `serviceKey, svyYr, schlId` (`academyinfo/update_academyinfo.py:1270-1279`)
- 429 대응:
  - 공통 재시도 `0 → 2 → 5 → 15 → 30초` (`academyinfo/include/common.py:155-175`, `academyinfo/COLLECTION_PLAN.md:121-125`)
  - `sync-school-indicators`만 배치 commit 후 중단 (`academyinfo/update_academyinfo.py:1226-1233`, `academyinfo/COLLECTION_PLAN.md:121-125`)

## career 실제 command surface
- CLI 명령: `plan`, `init-db`, `sync-code-list`, `sync-school-list`, `sync-subject-list`, `sync-aptitude-meta`, `sync-subject-detail`, `sync-job-list`, `sync-job-detail`, `sync-all` (`career/update_career.py:1385-1452`)
- 옵션:
  - `sync-subject-detail --school --seq --limit` (`career/update_career.py:1396-1399`)
  - `sync-job-list --keyword --max-pages` (`career/update_career.py:1401-1403`)
  - `sync-job-detail --seq --limit` (`career/update_career.py:1405-1407`)
  - `sync-all --keyword --max-pages --detail-limit --subject-detail-limit` (`career/update_career.py:1409-1413`)
- 실행 매핑:
  - `sync-code-list` → `themes`, `aptds`, `jobcodes` (`career/update_career.py:302-306`, `1048-1058`)
  - `sync-school-list` → 학교 목록 6종 (`career/update_career.py:309-316`, `653-672`)
  - `sync-subject-list` → 학과 목록 2종 (`career/update_career.py:319-322`, `704-720`)
  - `sync-subject-detail` → `subject_list` 기반 상세 확장 (`career/update_career.py:737-930`)
  - `sync-job-list` → `jobs` 목록 (`career/update_career.py:1061-1161`)
  - `sync-job-detail` → `job` 상세 (`career/update_career.py:1164-1374`)
  - `sync-aptitude-meta` → v2 tests + v2 test (`career/update_career.py:325-326`, `1008-1045`)
  - `sync-all` → `sync-code-list + sync-job-list + sync-subject-list + sync-job-detail + sync-subject-detail` (`career/update_career.py:1377-1382`, `1449-1450`)

## career 실제 endpoint/spec checklist
- 베이스 URL:
  - front JSON: `https://www.career.go.kr/cnet/front/openapi/{path}.json?apiKey=...` (`career/include/crawler_common.py:138-166`)
  - legacy JSON/XML: `https://www.career.go.kr/cnet/openapi/getOpenApi?...` (`career/include/crawler_common.py:146-171`, `career/update_career.py:499-514`)
  - aptitude v2: `https://www.career.go.kr/inspct/openapi/v2/tests`, `.../v2/test?q=...` (`career/update_career.py:543-554`, `1008-1013`, `career/APTITUDE_API_SPEC.md:126-185`)
- 코드 마스터 3종:
  - `themes`, `aptds`, `jobcodes` (`career/update_career.py:302-306`, `1048-1058`)
- 학교 목록 6종:
  - `elem_list`, `midd_list`, `high_list`, `univ_list`, `seet_list`, `alte_list` via legacy XML `svcCode=SCHOOL` (`career/update_career.py:309-316`, `653-672`)
- 학과 목록 2종:
  - `high_list`, `univ_list` via legacy XML `svcCode=MAJOR` (`career/update_career.py:319-322`, `704-720`)
- 학과 상세:
  - legacy XML `svcCode=MAJOR_VIEW`, `gubun={school_key}_list`, `majorSeq` (`career/update_career.py:737-745`)
- 직업 목록:
  - 우선 front `jobs`, 실패 시 legacy `svcCode=JOB&gubun=job_dic_list` (`career/update_career.py:1061-1073`)
- 직업 상세:
  - 우선 front `job?seq=...`, 실패 시 legacy `svcCode=JOB_VIEW&gubun=job_dic_list&jobdicSeq=...` (`career/update_career.py:1164-1172`)
- 적성검사 v2:
  - 목록 `GET /inspct/openapi/v2/tests`
  - 문항 `GET /inspct/openapi/v2/test?q={qno}`
  - 결과 `POST /inspct/openapi/v2/report`는 미구현 (`career/SERVICE_SPEC_STATUS.md:41-43`, `career/APTITUDE_API_SPEC.md:187-210`)

## 문서/코드 mismatch

### academyinfo
1. `academyinfo/COLLECTION_PLAN.md:147`은 `sync-startup-support`에 학교 배치 옵션을 "후속 과제"처럼 적었지만, 코드는 이미 `school_offset/school_limit`를 지원한다 (`academyinfo/update_academyinfo.py:1264-1280`, `1393-1403`).
2. `academyinfo` 문서군은 103개 스펙과 명령 분담이 대체로 코드와 일치한다. worker3 범위에서 큰 구조 mismatch는 위 1건 외에는 못 찾았다.

### career
1. `career/SERVICE_SPEC_STATUS.md:18`은 학교 정보에 대해 "서버 정기 cron 편성은 후속"이라 적었지만, `career/COLLECTION_PLAN.md:129-133,165-171`은 `sync-school-list`, `sync-subject-list` cron 등록/검증 완료로 기록한다.
2. `career/IMPLEMENTATION_SCOPE.md:46-59`는 2차 범위를 직업 상세 일부 + 학과 상세 일부로 좁게 적었지만, 실제 코드는 `interest_list`, `research_list`, `ability_list`, `depart_list`, `tag_list`, `job_rel_org_list`, `subject_text_list`, `subject_school_map`, `subject_feature_list`까지 적재한다 (`career/update_career.py:1357-1370`, `900-924`).
3. `career/COLLECTION_PLAN.md:46-51`은 학과 상세를 "확장 예정"으로 적었지만, 같은 문서 후반부와 코드에서는 이미 `sync-subject-detail` 구현/cron/스모크 완료 상태다 (`career/COLLECTION_PLAN.md:132,152-155,172-175`; `career/update_career.py:874-930`).
4. `career/SERVICE_SPEC_STATUS.md:20,41-43`의 적성검사 v2 "부분" 표기는 맞지만, 실제 명령 surface는 `sync-aptitude-meta` 단일이며 `sync-all`에는 포함되지 않는다 (`career/update_career.py:1016-1045`, `1377-1382`). 문서에 이 제한을 더 명시하는 편이 안전하다.

## 코드 리스크 / drift 포인트 (subagent 통합)
- academyinfo
  - `API_SPEC.md` 마크다운 패턴 의존 파서라 문서 형식이 바뀌면 엔드포인트가 조용히 누락될 수 있다 (`academyinfo/update_academyinfo.py:225-284`).
  - 분류되지 않은 신규 엔드포인트는 `school_indicator`로 떨어져 잘못된 파라미터 세트(`svyYr/schlId/[indctId]`)를 보낼 수 있다 (`academyinfo/update_academyinfo.py:320-341`, `1213-1227`).
  - `sync_regional_indicators()`의 `schlDivCd` 로딩 경로는 코드 체계 혼용 가능성이 있다 (`academyinfo/update_academyinfo.py:986-1007`, `1241-1258`).
- career
  - `sync-school-list`, `sync-subject-list`는 단일 페이지 호출이라 pagination drift에 취약하다 (`career/update_career.py:653-671`, `704-720`).
  - `sync-all`은 학교 목록/적성검사 메타를 포함하지 않아 명령명 대비 범위가 좁다 (`career/update_career.py:1377-1382`, `1428-1450`).
  - `sync_job_list()`는 list payload를 사실상 `jobs` 중심으로 보고 있어 shape drift 시 조기 종료 가능성이 있다 (`career/update_career.py:427-441`, `1149-1154`).

## TODO / 후속 문서 정합성
- `TODO.md` 미완료 최상단 우선순위는 이번 검토 결과와 충돌하지 않는다.
  - `academyinfo school_indicator_list` 429 완화/롤링 cron 안정화
  - `robocode-admin/db/` 모니터링 페이지 후속 구축
- `FOLLOWUP_NEXT_STEPS.md` 의 3개 바로 이어갈 작업(academyinfo 분할 cron 운영 확정, career 학교/학과 cron 검증, robocode-admin 데이터 계약 확정)은 현재 코드/문서/검증 결과와 정합하다.
- 이번 worker-3 범위에서는 공용 파일(`TODO.md`, `AGENTS.md`)을 직접 수정하지 않고 검증/증거 문서만 유지하는 편이 안전하다.

## 검증
- PASS `python3 -m py_compile academyinfo/update_academyinfo.py career/update_career.py`
- PASS `python3 academyinfo/update_academyinfo.py plan`
- PASS `python3 career/update_career.py plan`
- PASS `python3 -m pytest academyinfo/tests/test_update_academyinfo.py career/tests/test_update_career.py` → `13 passed in 0.07s`
- PASS `python3 -m unittest academyinfo.tests.test_update_academyinfo career.tests.test_update_career` → `Ran 13 tests in 0.085s / OK`
- FAIL `python3 -m ruff check academyinfo/update_academyinfo.py career/update_career.py worker-3-task-3-summary.md` → `No module named ruff`
- N/A end-to-end 실호출 검증은 read-only 분석 작업 범위를 넘고 API 키/DB 의존이 있어 수행하지 않음

## 작업 메모
- Subagent skip reason: 이번 task-3는 기존 코드/문서/테스트 산출물의 교차 검증과 증거 문서 갱신이 핵심이라, 별도 하위 에이전트 fan-out보다 단일 워커의 직렬 검토가 더 안전했다.
