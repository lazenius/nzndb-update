# Academyinfo 수집/DB 구축 구현 범위 및 검증 계획

## 기준 산출물

- API 명세 초안: `academyinfo/API_SPEC.md`
- 스키마 초안: `academyinfo/DB_SCHEMA.md`
- URL 목록: `academyinfo/README.md`

## 현재 상태 점검

- 이 로컬 프로젝트는 실제 수집기 저장소가 아니라 문서 기준점이다.
- 지금 확보한 근거는 공공데이터포털 공개 페이지의 embedded Swagger 명세다.
- 따라서 현재 단계 산출물은 **개발 가능한 수준의 명세 + DB 초안 + 구현 우선순위**까지다.

---

## 구현 범위

### 1차 구현 범위

1. 코드/년도 수집
   - 대상: `code_list`, `year_list`
   - 범위: 지역, 설립유형, 학교유형, 학교종류, 계열, 학위과정, 주야간, 조사/공시년도
2. 학교 기본정보 수집
   - 대상: `school_list`
   - 범위: 대학코드조회, 대학 및 전문대학정보, 대학 검색목록 계열
3. 학과 기본정보 수집
   - 대상: `subject_list`
   - 범위: 대학 학과 정보 코드조회 + 대학별 학과정보
4. 학교별 핵심 지표 수집
   - 대상: `school_indicator_list`
   - 범위: 교육여건, 교원·연구, 학생, 재정 API의 대학비교통계/우리대학경쟁력 계열

### 2차 구현 범위

1. 지역별 통계 수집
   - 대상: `regional_indicator_list`
   - 범위: `getRegional*` 계열 전체
2. 학교별 지표 정규화
   - `val1`~`val10` 구조를 지표별 세로 테이블로 재분해할지 검토
3. 결측/반복 정책 고정
   - `body.items.item` 단건/배열 직렬화 정책
   - 빈 문자열/0/null 저장 규칙
4. 지역 PK 보조키 확정
   - `regional_indicator_list`의 `znNmRmk`(`region_rmk`)를 PK/unique key에 포함할지 실응답 기준으로 확정
5. 연도별 코드체계 추적 여부 확정
   - `getCodeBySeriesSystem`의 `svyYr`를 `code_list`에 저장할지 결정
6. 학과 보조 코드 중복 저장 여부 확정
   - `psbsDivCd`, `schlEstbDivCd`, `schlMjrCharCd`, `schlMjrStatCd`, `schlKndCd`를 `subject_list`에 직접 둘지, `school_list`/코드 테이블 join 정책으로 고정

### 3차 구현 범위

1. 산학협력/창업지원 7개 API 적재
   - 대상: `startup_support_list` 또는 세부 분해 테이블
2. 지표 메타 정규화
   - 지표명/설명/출처를 별도 마스터로 관리할지 결정
3. 증분 수집 정책
   - 연도별 전체 재수집 vs 학교별 변경분 갱신
4. 선택 컬럼 슬림화 검토
   - `school_indicator_list.apy_yr`처럼 일부 API 전용 컬럼은 유지하되 적용 범위를 문서와 코드에 명시

### 구현 제외 범위

- 웹 UI
- 운영/모니터링 화면
- 배포 자동화
- 실제 운영 API 키 발급/권한 관리 절차 문서화

---

## 수집기 구조 초안

### 요청 단위

1. 코드/년도 선수집
2. 학교 마스터 수집
3. 학과 마스터 수집
4. 학교별 지표 수집
5. 지역별 지표 수집
6. 산학협력 수집

### 공통 파라미터 빌더

- `serviceKey`
- `pageNo`
- `numOfRows`
- `svyYr`
- `schlId`
- `schlDivCd`
- 일부 API의 `indctId`

### 적재 전략

- 코드/년도: 전체 교체 또는 upsert
- 학교/학과: `(schl_id, svy_yr)` / `(schl_id, svy_yr, major_id)` 기준 upsert
- 학교별 지표: `(api_id, indct_id, schl_id, svy_yr)` 기준 upsert
- 지역별 지표: 우선 `(api_id, indct_id, schl_div_cd, region_name, region_rmk)` 기준 검토 후 upsert

---

## 구현 전 확인 필요 항목

1. 실제 응답 포맷 확인
   - Swagger는 XML 기준이다.
   - JSON 지원 여부는 실제 호출로 확인 필요
2. 필수 파라미터 조합 확인
   - `schlKrnNm` required 표기가 있는 표준데이터셋 API는 실제로 `schlId`만으로 되는지 확인 필요
3. 페이지네이션 상한 확인
   - `numOfRows` 최대값
   - 총 페이지 수
4. 산학협력 API 필드 확정
   - 현재는 key-value 임시 설계 수준
5. 운영 수집 단위 확정
   - 연도 전체
   - 학교 단위 재수집
   - 실패 페이지 재시도 단위
6. 학과/코드 중복 저장 정책 확정
   - `subject_list`에 코드성 컬럼을 직접 둘지
   - `school_list`/`code_list` join으로만 조회할지

---

## 단계별 작업 순서 (상세)

> 코드/배포 작업 없이 명세·설계 단계에서 수행 가능한 사항을 기준으로 작성.
> 각 단계 완료 후 아래 검증 체크리스트로 완료 여부를 확인한다.

### Phase 0 — 사전 준비

1. **API 키 확보**
   - 공공데이터포털에서 9개 서비스 각각 활용신청 또는 일괄 신청 여부 결정
   - 개발용 키와 운영용 키를 분리할지 결정
   - 키 저장 방식 결정 (환경변수 `.env` vs 설정파일)

2. **DB 인스턴스 결정**
   - `ACADEMYINFO_DB` 생성 대상 서버 확정 (로컬 MySQL / AWS RDS)
   - 접속 계정 및 권한 결정
   - 문자셋: `utf8mb4`, `utf8mb4_unicode_ci` 확정

3. **응답 포맷 사전 확인**
   - 9개 서비스 중 대표 엔드포인트 1개씩(`getUniversityCode`, `getSchoolInfo`, `getSchoolMajorInfo`) 수동 curl 호출
   - XML/JSON 지원 여부 확인 (`_type=json` 파라미터 여부)
   - `body.items.item` 단건 vs 배열 처리 방식 확인 (실제 응답 기준으로 `DB_SCHEMA.md`의 직렬화 정책 갱신)

4. **페이지네이션 상한 확인**
   - `getUniversityCode` 기준 `numOfRows=1000` 요청 후 `totalCount` 확인
   - 한 번에 전체 수집 가능한 최대 `numOfRows` 확정
   - 멀티페이지 필요 여부 결정

---

### Phase 1 — 코드/년도 마스터 (1차)

순서:
1. `getCodeByRegion` — 지역코드 수집 → `code_list` (code_type='region')
2. `getCodeByFound` — 설립유형 수집 → `code_list` (code_type='found')
3. `getCodeByType` — 학교유형 수집 → `code_list` (code_type='school_type')
4. `getCodeByKind` — 학교종류 수집 → `code_list` (code_type='school_kind')
5. `getNoticeSvyYear` — 조사년도 수집 → `year_list` (year_type='notice_svy')
6. `getComparisonPubYear` — 공시년도 수집 → `year_list` (year_type='comparison_pub')
7. `getKeyIndicatorCode` — 주요지표 코드 수집 → `code_list` (code_type='key_indicator')

완료 기준: 7개 API 호출 성공, `code_list` / `year_list` 행 수가 각 응답 `totalCount`와 일치.

---

### Phase 2 — 학교 마스터 (1차)

순서:
1. `year_list`에서 수집 대상 `svyYr` 목록 로드
2. `getUniversityCode` — 전체 대학코드 수집 → `school_list` (기본키: `schl_id`, `svy_yr`)
3. `getSchoolInfo` — 대학 및 전문대학 상세정보 수집 → `school_list` merge
4. `getNoticeUniversitySearchList` — 우리대학경쟁력 학교목록 → `school_list` merge
5. `getComparisonUniversitySearchList` — 대학비교통계 학교목록 → `school_list` merge

완료 기준: 수집된 `schl_id` 수가 `getUniversityCode` `totalCount`와 일치. `schlKrnNm` 누락 없음.

---

### Phase 3 — 학과 마스터 (1차)

순서:
1. `getUniversityMajorFieldCode` (BasicInformationService_1) — 학과 코드 수집 → `code_list` (code_type='major_field')
2. `school_list`에서 `schl_id` 목록 로드
3. `getSchoolMajorInfo` — 학교별 학과정보 수집 → `subject_list` (기본키: `schl_id`, `svy_yr`, `major_id`)

완료 기준: 수집된 `schl_id`/학과 조합이 `getSchoolMajorInfo` `totalCount` 합산과 일치.

---

### Phase 4 — 학교별 핵심 지표 (1차)

수집 대상 API (대학비교통계/우리대학경쟁력 계열 각 서비스당 대표 지표 1개씩 우선):

| 서비스 | 대표 엔드포인트 | 비고 |
|---|---|---|
| EducationConditionService | `getComparisonSchoolGroundsAndBdsEnsureRate` | 교지·교사 확보율 |
| EducationResearchService | `getComparisonFullTimeFacultyEnsureCrntSt` | 전임교원 확보 현황 |
| StudentService | `getComparisonFreshmanChanceBalanceSelectionRatio` | 신입생 기회균형 |
| FinancesService | (API_SPEC 확인 후 추가) | 재정 대표 지표 |

순서:
1. `school_list`에서 `schl_id` 목록 + `year_list`에서 `svy_yr` 목록 로드
2. (schl_id, svy_yr) 조합을 순회하며 각 엔드포인트 호출
3. 응답 `indctId`, `indctVal1` → `school_indicator_list` upsert
4. `getComparisonFullTimeFacultyResearchCrntSt` (indctId 필수) — `getKeyIndicatorCode`로 사전 확보한 `cdid` 목록으로 순회

완료 기준:
- 대표 4개 엔드포인트 호출 성공
- `school_indicator_list`에 `api_id`, `indct_id`, `schl_id`, `svy_yr` 4-tuple PK 기준 중복 없음
- 재수집 시 PK 충돌 없이 upsert 동작 확인

---

### Phase 5 — 지역별 통계 (2차)

순서:
1. `code_list` (code_type='school_type')에서 `schlDivCd` 목록 로드
2. `getRegional*` 계열 엔드포인트 순서대로 호출 (EducationConditionService 6개 → EducationResearchService 9개 → StudentService → FinancesService 순)
3. 응답 `fieldType1~7` / `fieldVal1~7` → `regional_indicator_list` upsert

완료 기준: 각 `getRegional*` 호출 성공, `regional_indicator_list`에 `(api_id, indct_id, schl_div_cd, region_name)` 중복 없음.
실응답에서 `znNmRmk`가 구분자 역할을 하면 `region_rmk` 포함 unique/PK로 확정.

---

### Phase 6 — 산학협력 (3차)

전제: 실응답 확보 후 필드 확정 필요.

순서:
1. `IndustryAcademicCooperationService` 7개 엔드포인트 응답 샘플 수동 수집
2. `startup_support_list` 컬럼 확정 후 `DB_SCHEMA.md` 갱신
3. 수집기 구현

완료 기준: 7개 엔드포인트 응답 샘플 확보, `DB_SCHEMA.md` 산학협력 섹션 확정.

---

## 단계별 검증 체크리스트

### Phase 0 — 사전 준비 체크리스트

- [ ] API 키 발급 또는 테스트 키 확보 완료
- [ ] DB 서버/계정/문자셋 확정 및 `ACADEMYINFO_DB` 생성 가능한 상태
- [ ] `getUniversityCode` 수동 curl 호출 → HTTP 200 + resultCode `00` 확인
- [ ] `getSchoolInfo` 수동 호출 → 응답 포맷(XML/JSON) 확인
- [ ] `getSchoolMajorInfo` 수동 호출 → `body.items.item` 단건/배열 케이스 확인
- [ ] `numOfRows` 상한 결정 (100/500/1000 중 허용 최대값)
- [ ] `DB_SCHEMA.md`의 직렬화 정책(`item` 단건/배열 처리) 실응답 기준으로 검토 완료
- [ ] `getCodeBySeriesSystem` 수동 호출 또는 샘플 확보 → `svyYr` 저장 필요 여부 결정
- [ ] 지역별 API 샘플 확보 → `znNmRmk`가 PK 구분자인지 확인

### Phase 1 — 코드/년도 체크리스트

- [ ] 7개 코드 API 모두 호출 성공 (resultCode `00`)
- [ ] `code_list` 행 수 = 각 API `totalCount` 합산
- [ ] `year_list` 행 수 = `getNoticeSvyYear` + `getComparisonPubYear` totalCount 합산
- [ ] upsert 재실행 시 행 수 변화 없음 (멱등성)
- [ ] `code_list` (code_type='key_indicator') 행 수 > 0

### Phase 2 — 학교 마스터 체크리스트

- [ ] `getUniversityCode` 전체 페이지 수집 완료 (pageNo 순회 확인)
- [ ] `school_list` 행 수 = `getUniversityCode` totalCount 이상
- [ ] `schlKrnNm` null 행 없음
- [ ] `schl_id` + `svy_yr` 복합 PK 중복 없음
- [ ] `getNoticeUniversitySearchList`, `getComparisonUniversitySearchList` 결과가 기존 행과 정합성 확인

### Phase 3 — 학과 마스터 체크리스트

- [ ] 학과 코드 API 호출 성공
- [ ] `subject_list` — 최소 1개 `schl_id` 대상으로 `getSchoolMajorInfo` 호출 성공
- [ ] 응답 `totalCount` > 0
- [ ] `(schl_id, svy_yr, major_id)` PK 중복 없음
- [ ] upsert 재실행 후 PK 충돌 없음

### Phase 4 — 학교별 핵심 지표 체크리스트

- [ ] 대표 4개 엔드포인트 각 1건 이상 성공 응답
- [ ] `school_indicator_list` — `(api_id, indct_id, schl_id, svy_yr)` PK 기준 upsert 성공
- [ ] 동일 연도 재수집 시 행 수 변화 없음
- [ ] 원문 응답 `indctVal1` 값과 DB 저장값 1건 대조 일치
- [ ] `indctId` 필수 파라미터 필요 엔드포인트 처리 확인 (`getComparisonFullTimeFacultyResearchCrntSt`, `getComparisonFullTimeFacultyEnsureCrntSt`)

### Phase 5 — 지역별 통계 체크리스트

- [ ] `getRegional*` 계열 최소 3개 엔드포인트 호출 성공
- [ ] `fieldType1~7` / `fieldVal1~7` 저장 정책 결정 및 적용 (`regional_indicator_list`)
- [ ] `(api_id, indct_id, schl_div_cd, region_name)` PK 중복 없음
- [ ] upsert 재실행 후 PK 충돌 없음
- [ ] `znNmRmk` 값이 있는 응답 샘플 확인
- [ ] 필요 시 `(api_id, indct_id, schl_div_cd, region_name, region_rmk)` 기준으로 PK/unique 재확정

### Phase 2~3 공통 설계 체크리스트

- [ ] `subject_list`에 본분교/설립구분/학교종류/학과상태/학과특성 코드값을 직접 저장할지 결정
- [ ] 직접 저장하지 않으면 `school_list`/`code_list` join 정책을 문서에 명시
- [ ] `school_indicator_list.apy_yr` 적용 API 목록을 구현 문서에 명시

### Phase 6 — 산학협력 체크리스트

- [ ] 7개 엔드포인트 수동 호출 성공 + 샘플 응답 저장
- [ ] 응답 필드 구조 분석 완료
- [ ] `DB_SCHEMA.md` 산학협력 섹션 `startup_support_list` 컬럼 확정
- [ ] upsert 기준키 결정

---

## 문서 정합성 체크리스트

> 문서 단계에서 수행하는 크로스체크. 코드 작성 전 완료 권장.

- [ ] `API_SPEC.md`의 9개 서비스가 `DB_SCHEMA.md` 테이블 범위에 모두 매핑됨
- [ ] `README.md`의 URL 9개가 `API_SPEC.md`에 모두 반영됨
- [ ] 1차/2차/3차 범위가 `DB_SCHEMA.md` 1차/확장 구분과 일치함
- [ ] `school_indicator_list` upsert 기준키(`api_id`, `indct_id`, `schl_id`, `svy_yr`)가 `DB_SCHEMA.md` PK와 일치함
- [ ] Phase 0 "구현 전 확인 필요 항목" 5개가 모두 답변된 상태로 갱신됨
- [ ] `getComparisonFullTimeFacultyResearchCrntSt` (indctId 필수 파라미터) 처리 방식이 Phase 4 작업 순서에 반영됨
- [ ] 산학협력 API는 실응답 확보 전까지 컬럼 미확정 상태임이 `DB_SCHEMA.md`에 명시됨

---

## 결정

- 지금 단계에서는 **학교/학과/학교별 지표**까지를 구현 착수 기준으로 본다.
- 지역별 통계는 2차, 산학협력은 3차로 미룬다.
- 산학협력 API는 실응답 확보 전까지 세부 컬럼을 확정하지 않는다.
- Phase 0 사전 확인 항목은 수집기 코드 작성 전 모두 해소한다.
