# API_SPEC ↔ DB_SCHEMA 매핑 누락 점검 보고서

- 작성: worker-1 (2026-06-25)
- 기준: `API_SPEC.md` (9개 서비스, 103개 엔드포인트), `DB_SCHEMA.md` (7개 테이블)

---

## 요약

| 항목 | 대상 테이블 | 심각도 | 내용 |
|------|-------------|--------|------|
| G1 | `subject_list` | **High** | `schlMjrId`(학교별 학과 ID) 컬럼 없음 |
| G2 | `subject_list` | **High** | 표준분류 코드 3단계 (`srsSclftCd`, `srsMclftCd`, `srsLclftCd`) 컬럼 없음 |
| G3 | `subject_list` | **High** | 표준분류 계열 한글명 3단계 (`korSrsSclftNm`, `korSrsMclftNm`, `korSrsLclftNm`) 컬럼 없음 |
| G4 | `startup_support_list` | **High** | `indctId`, `indctYr` 컬럼 없음 |
| G5 | `school_list` | **Medium** | 두 API 이원화 merge 정책 미정의 |
| G6 | `code_list` | **Medium** | `getCodeBySeriesSystem` 의 `svyYr` 추적 불가 |
| G7 | `subject_list` | **Medium** | 본분교/설립구분 코드 컬럼 없음 |
| G8 | `regional_indicator_list` | **Medium** | PK에 `znNmRmk` 미포함 → 중복 위험 |
| G9 | `subject_list` | **Low** | 코드성 컬럼 명칭만 있고 코드값 없음 |
| G10 | `school_indicator_list` | **Low** | `apy_yr` 컬럼 적용 API가 1개만 있음 |

---

## 상세 내용

### G1 — `subject_list`: `schlMjrId` 컬럼 없음 (High)

**원천 API**: `/getUniversityMajorCode` (BasicInformationService_1)

**응답 필드**: `schlMjrId` — 학교가 자체 부여하는 학과 고유 식별자. `kediMjrId`(표준화 ID)와 별개.

**현재 스키마**: `subject_list.major_id = kediMjrId`. `schlMjrId` 컬럼 없음.

**영향**:
- `kediMjrId`는 여러 학교가 공유하거나 동일 학교 내 복수 학과가 같은 값을 가질 수 있음
- PK `(schl_id, svy_yr, major_id)` 충돌 위험
- 수집기에서 `/getUniversityMajorCode` 재조회 시 `schlMjrId` 기준 upsert 불가

**권고**: `subject_list`에 `schl_mjr_id varchar(30)` 추가 또는 PK 구성 재검토

---

### G2 — `subject_list`: 표준분류 계열 코드 3단계 컬럼 없음 (High)

**원천 API**: `/getUniversityMajorCode` (BasicInformationService_1)

**응답 필드**: `srsLclftCd`(대계열), `srsMclftCd`(중계열), `srsSclftCd`(소계열)

**현재 스키마**: 없음. `oneself_series_name`(대학자체계열명)만 있음.

**영향**: 표준분류 계열별 집계/필터 쿼리 불가. 단순 명칭만 있어 코드 기반 조인 불가.

**권고**: `srs_lclft_cd`, `srs_mclft_cd`, `srs_sclft_cd` 컬럼 3개 추가

---

### G3 — `subject_list`: 표준분류 계열 한글명 3단계 컬럼 없음 (High)

**원천 API**: `/getUniversityMajorCode` (BasicInformationService_1)

**응답 필드**: `korSrsLclftNm`(대계열명), `korSrsMclftNm`(중계열명), `korSrsSclftNm`(소계열명)

**현재 스키마**: 없음.

**영향**: 표준분류 계열 명칭을 code_list join 없이 직접 조회 불가. 보고서 출력 시 항상 code_list join 필요.

**권고**: `srs_lclft_name`, `srs_mclft_name`, `srs_sclft_name` 컬럼 추가 (code_list join 최소화 목적)

---

### G4 — `startup_support_list`: `indctId`, `indctYr` 컬럼 없음 (High)

**원천 API**: 산학협력 7개 API 전체 (`getCntrctmjrInstOperCstt`, `getOrdmthEdcCrseInstOper`, `getGrndsPrcOperCstt`, `getCsptDsgnOperCstt`, `getTcherStupSuptCstt`, `getStdnStupSuptCstt`, `getStupEdcSuptCstt`)

**응답 필드**: `indctId`, `indctYr` — 모든 산학협력 API 응답에 공통 포함

**현재 스키마**:
```sql
PRIMARY KEY (api_id, schl_id, svy_yr, seq, item_key)
-- item_key, item_value로 key-value 저장
```

**영향**:
- `indctId` 기준으로 산학협력 지표를 구분할 수 없음
- `indctYr` 정보가 유실됨
- `seq` 대신 `indctId`를 고유키로 쓰는 것이 더 자연스러운 설계

**권고**: 컬럼 `indct_id varchar(30)`, `indct_yr char(4)` 추가. PK에 `seq` 대신 `indct_id` 사용 검토

---

### G5 — `school_list`: 두 API 이원화 merge 정책 미정의 (Medium)

**원천 API**:
- `/getUniversityCode` (BasicInformationService_2): `schlId`, `svyYr`, `clgcpDivCd`, `clgcpDivNm`, `estbDivCd`, `estbDivNm`, `schlDivCd`, `schlDivNm`, `schlFullNm`, `schlKrnNm`, `znCd`, `znNm`, `schlKndCd`, `schlKndNm` 제공
- `/getSchoolInfo` (SchoolInfoService): `lstUpdtDtm`, `pbnfAreaCd`, `pbnfAreaNm`, `postNo`, `postNoAdrs`, `psbsDivNm`, `schlDivNm`, `schlEngNm`, `schlEstbDivNm`, `schlEstbDt`, `schlId`, `schlKndNm`, `schlNm`, `schlRepFxNoCtnt`, `schlRepTpNoCtnt`, `schlUrlAdrs`, `svyYr` 제공

**문제**:
- `/getUniversityCode`에는 코드값(div_cd, kind_cd, est_cd, campus_cd 등) 있으나 주소/URL/전화 없음
- `/getSchoolInfo`에는 주소/URL/전화 있으나 코드값(`schlDivCd`, `schlKndCd`, `schlEstbDivCd`) 없음
- `school_list` 1개 row를 완성하려면 두 API 결과를 `(schl_id, svy_yr)` 기준으로 merge해야 함
- 스키마 문서와 IMPLEMENTATION_SCOPE.md에 이 merge 로직 미정의

**권고**: IMPLEMENTATION_SCOPE.md에 수집 순서(`getUniversityCode` 먼저 upsert → `getSchoolInfo` 보완 upsert) 명시

---

### G6 — `code_list`: `getCodeBySeriesSystem` 응답의 `svyYr` 추적 불가 (Medium)

**원천 API**: `/getCodeBySeriesSystem` (BasicInformationService_1)

**응답 필드**: `svyYr`, `srsLclftCd`, `srsMclftCd`, `srsSclftCd`

**현재 스키마**: `code_list` PK = `(code_type, code)`. `svyYr` 컬럼 없음.

**문제**:
- 계열체계 코드는 조사년도별로 변경될 수 있음
- `svyYr`를 저장하지 않으면 연도별 변경 추적 불가
- 단순 (code_type, code) upsert 시 최신 연도 값으로 덮어쓰기

**권고**: `code_list`에 `svy_yr char(4)` 컬럼 추가 (선택). 또는 year_type 컬럼을 활용해 계열체계 코드는 year_type을 포함하는 code_type으로 구분

---

### G7 — `subject_list`: 본분교/설립구분 코드 컬럼 없음 (Medium)

**원천 API**: `/getUniversityMajorCode` (BasicInformationService_1)

**응답 필드**: `psbsDivNm`, `psbsDivCd`(본분교구분), `schlEstbDivNm`, `schlEstbDivCd`(설립구분)

**현재 스키마**: 없음.

**영향**: 학과 레벨에서 본분교/설립구분을 직접 조회 불가. school_list join 필요.

**권고**: 필요시 `campus_div_name`, `campus_div_cd`, `estb_div_name`, `estb_div_cd` 추가. 불필요하면 school_list join 정책 명시.

---

### G8 — `regional_indicator_list`: PK에 `znNmRmk` 미포함 (Medium)

**원천 API**: `/getRegionalBasicPropertiesForProfitBurdenRate`, `/getRegionalStudentForPersonDataPurchasePrice` 등 일부 3개년도 비교형 지역별 API

**응답 구조**: `znNm`(지역명), `znNmRmk`(지역명 비고)가 별도 필드로 존재

**현재 스키마**: PK = `(api_id, indct_id, schl_div_cd, region_name)`. `region_name`이 `znNm`에 대응.

**문제**: `znNm`이 동일한데 `znNmRmk`가 다른 행(예: 동일 지역의 소규모학교 vs 대규모학교 비고)이 있을 경우 PK 충돌. `znNmRmk`가 실제로 구분자 역할을 하는지 실응답 확인 필요.

**권고**: 실응답 확인 후 PK 또는 unique key에 `region_rmk` 포함 여부 결정

---

### G9 — `subject_list`: 코드 컬럼 명칭만 있고 코드값 없음 (Low)

**원천 API**: `/getUniversityMajorCode`

**응답 필드**:
- `schlMjrCharCd`(학과특성코드), `schlMjrCharNm`(학과특성명)
- `schlMjrStatCd`(학과상태코드), `schlMjrStatNm`(학과상태명)
- `schlKndCd`(학교종류코드), `schlKndNm`(학교종류명)

**현재 스키마**: `major_char_name`, `major_stat_name`, `school_kind_name` 컬럼만 있고, 대응 코드값 컬럼 없음.

**영향**: 코드 기반 필터/집계 불가. code_list join만으로 역방향 코드 조회 필요.

**권고**: `major_char_cd`, `major_stat_cd`, `school_kind_cd` 컬럼 추가 (선택)

---

### G10 — `school_indicator_list`: `apy_yr` 적용 API 1개 (Low)

**원천 API**: `/getNoticeGraduateEmploymentRate` (StudentService) — `apyYr` 필드 포함
그 외 `Notice*` 계열 API들 — `apyYr` 없음

**현재 스키마**: `school_indicator_list.apy_yr` 컬럼 존재.

**영향**: `apy_yr`가 적용되는 API가 1개뿐임에도 컬럼이 있어 혼동 가능.

**권고**: `apy_yr` 컬럼 유지하되, `getNoticeGraduateEmploymentRate` 전용임을 문서에 명시.

---

## 매핑 현황 (문제 없는 항목)

- **code_list**: `getCodeByRegion`, `getCodeByFound`, `getCodeByType`, `getCodeByKind`, `getCodeByLargeSeries`, `getCodeByMiddleSeries`, `getCodeBySmallSeries`, `getCodeByPrincipalSchoolBranchSchool`, `getCodeByLessonTerm`, `getCodeByDegreeCourse`, `getCodeByDayAndNight`, `getCodeByCollege`, `getCodeByMajorStatus`, `getCodeByMajorCharacter`, `getCodeByOneselfSeries` → `(code_type, code, name)` 패턴으로 일관 매핑 가능 ✓
- **year_list**: `getNoticeSvyYear`, `getComparisonPubYear` → `(year_type, year_val)` 매핑 ✓
- **school_list**: 두 API 조합으로 전체 컬럼 채울 수 있음 (G5 정책만 정의하면 됨) ✓
- **subject_list 기본 필드**: `kediMjrId`, `stdClftMjrId`, `korMjrNm`, `clgNm`, `mjrAreaCd`, `mjrAreaNm`, `mjrAreaSignguNm`, `pbnfDgriCrseDivNm`, `lsnTrmNm`, `onsfSrsClftNm`, `eschlPscpNum`, `grdtNum`, `edcCrseLtrCtnt`, `pwayEmplLtrCtnt` 등 → 매핑 가능 ✓
- **school_indicator_list**: 대학비교통계/우리대학경쟁력 계열 (교육여건, 교원연구, 학생, 재정) → `val1`~`val10` 범위 내 (최대 4개 valN 필드) ✓
- **regional_indicator_list**: `getRegional*` 계열 → `field_type1`~`field_type7`, `field_val1`~`field_val7` 또는 3개년도 비교 구조로 매핑 가능 ✓
- **startup_support_list**: 산학협력 7개 API의 `indctVal1`~`indctVal25` → key-value 구조로 수용 가능 (G4 컬럼만 추가하면 됨) ✓

---

## 우선 조치 권고

1. **즉시**: `subject_list`에 `schl_mjr_id`, `srs_lclft_cd`, `srs_mclft_cd`, `srs_sclft_cd` 추가 (G1, G2)
2. **구현 전**: `startup_support_list`에 `indct_id`, `indct_yr` 추가 (G4)
3. **문서화**: IMPLEMENTATION_SCOPE.md에 `school_list` 이원화 merge 수집 순서 명시 (G5)
4. **실응답 후 결정**: `regional_indicator_list` PK 구조 확정 (G8), `code_list` svyYr 여부 (G6)
