# Academyinfo 서비스/스펙/DB/수집기 상태

## 기준

- 기준 문서: `academyinfo/API_SPEC.md`, `academyinfo/DB_SCHEMA.md`, `academyinfo/IMPLEMENTATION_SCOPE.md`, `academyinfo/COLLECTION_PLAN.md`
- 기준 코드: `academyinfo/update_academyinfo.py`
- 상태 표기:
  - `예` = 현재 기준 저장소/서버에서 구축 또는 개발됨
  - `부분` = 임시 적재/정규화 미확정/부분 검증 상태
  - `아니오` = 아직 없음

## 서비스 요약

| 서비스 | 스펙 수 | 관련 DB | DB 구축여부 | 수집프로그램 개발여부 | 비고 |
|---|---:|---|---|---|---|
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | 10 | code_list, school_list, year_list | 예 | 예 | 학교 마스터 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | 12 | regional_indicator_list, school_indicator_list | 예 | 예 | 학교 지표 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | 22 | regional_indicator_list, school_indicator_list | 예 | 예 | 학교 지표 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | 27 | regional_indicator_list, school_indicator_list | 예 | 예 | 학교 지표 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | 10 | regional_indicator_list, school_indicator_list | 예 | 예 | 학교 지표 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | 13 | code_list, raw + code_list(검토중), subject_list | 부분 | 부분 | 학과 코드/기준정보 계열 |
| 7. 한국대학교육협의회_대학별 학과정보_GW | 1 | subject_list | 예 | 예 | 학교별 학과 목록 본체 |
| 8. 한국대학교육협의회_대학 및 전문대학정보_GW | 1 | school_list | 예 | 예 | 학교 상세 merge 소스 |
| 9. 한국대학교육협의회_대학알리미 산학협력 현황_GW | 7 | startup_support_list | 부분 | 부분 | 산학협력 7개 API, key-value 임시 적재 |

## 스펙별 상태

| 서비스 | 스펙 | 분류 | 관련 DB | DB 구축여부 | 수집프로그램 개발여부 | 비고 |
|---|---|---|---|---|---|---|
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `/getUniversityCode` | 학교 마스터 | `school_list` | 예 | 예 | 학교 기본 마스터 적재 |
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `/getCodeByRegion` | 메타데이터 | `code_list` | 예 | 예 | 코드성 메타 수집 |
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `/getNoticeUniversitySearchList` | 학교 마스터 | `school_list` | 예 | 예 | 학교 보강 merge |
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `/getComparisonUniversitySearchList` | 학교 마스터 | `school_list` | 예 | 예 | 학교 보강 merge |
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `/getKeyIndicatorCode` | 메타데이터 | `code_list` | 예 | 예 | 주요지표 코드 수집 |
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `/getComparisonPubYear` | 메타데이터 | `year_list` | 예 | 예 | 공시년도 수집 |
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `/getCodeByFound` | 메타데이터 | `code_list` | 예 | 예 | 코드성 메타 수집 |
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `/getNoticeSvyYear` | 메타데이터 | `year_list` | 예 | 예 | 조사년도 수집 |
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `/getCodeByType` | 메타데이터 | `code_list` | 예 | 예 | 코드성 메타 수집 |
| 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `/getCodeByKind` | 메타데이터 | `code_list` | 예 | 예 | 코드성 메타 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getComparisonLibraryBudgetCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getComparisonDormitoryAcceptanceCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getComparisonBasicPropertiesForProfitBurdenRate` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getComparisonBasicPropertiesForprofitCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getComparisonStudentForPersonDataPurchasePrice` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getComparisonSchoolGroundsAndBdsEnsureRate` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getRegionalSchoolGroundsAndBdsEnsureRate` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getRegionalDormitoryAcceptanceCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getRegionalLibraryBudgetCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getRegionalBasicPropertiesForProfitBurdenRate` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getRegionalBasicPropertiesForprofitCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW | `/getRegionalStudentForPersonDataPurchasePrice` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getComparisonGypsyScholarFacultyLectureChargeRatio` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getRegionalGypsyScholarFacultyLectureChargeRatio` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getComparisonForeignFullTimeFacultyCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getRegionalForeignFullTimeFacultyCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getComparisonFullTimeFacultyForPersonBookTranslatedBook` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getRegionalFullTimeFacultyForPersonBookTranslatedBook` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getComparisonFullTimeFacultyForPersonStudentNumberEnrolledStudent` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getRegionalFullTimeFacultyForPersonStudentNumberEnrolledStudent` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getComparisonFullTimeFacultyForPersonStudentNumberFixedNumber` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getRegionalFullTimeFacultyForPersonStudentNumberFixedNumber` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getComparisonLectureChargeRatio` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getRegionalLectureChargeRatio` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getComparisonFullTimeFacultyInsideOfSchoolForPersonResearchGrant` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getRegionalFullTimeFacultyInsideOfSchoolForPersonResearchGrant` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getComparisonFullTimeFacultyOutsideOfSchoolForPersonResearchGrant` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getRegionalFullTimeFacultyOutsideOfSchoolForPersonResearchGrant` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getComparisonFullTimeFacultyResearchCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getNoticeFullTimeFacultyResearchCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getRegionalFullTimeFacultyResearchCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getComparisonFullTimeFacultyEnsureCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getRegionalFullTimeFacultyEnsureCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `/getNoticeFullTimeFacultyEnsureRate` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonFreshmanChanceBalanceSelectionRatio` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalFreshmanChanceBalanceSelectionRatio` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonFreshmanEnsureCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalFreshmanEnsureCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getNoticeFreshmanDrafteesRate` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonForeignDropOutCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalForeignDropOutCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonForeignStudentCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalForeignStudentCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonEntranceModelLastRegistrationRatio` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalEntranceModelLastRegistrationRatio` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonEnrolledStudentCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalEnrolledStudentCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getNoticeEnrolledStudentDrafteesRate` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonEnrolledStudentEnsureRate` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalEnrolledStudentEnsureRate` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonEnrolledStudent` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalEnrolledStudent` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonInsideFixedNumberFreshmanCompetitionRate` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalInsideFixedNumberFreshmanCompetitionRate` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalGraduateEnterFindJobCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getNoticeGraduateEmploymentRate` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonDropOutStudentCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalDropOutStudentCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getNoticeStudentsWastageRate` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getComparisonStudentOnALeaveOfAbsence` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 4. 한국대학교육협의회 대학정보공시 학생 현황_GW | `/getRegionalStudentOnALeaveOfAbsence` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | `/getComparisonTuitionCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | `/getComparisonScholarshipBenefitCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | `/getComparisonEducationalExpensesReductionCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | `/getRegionalEducationalExpensesReductionCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | `/getComparisonEducationExpensesLoanCrntSt` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | `/getComparisonEducationExpensesLoanUseStudentRatioTuition` | 학교 지표 | `school_indicator_list` | 예 | 예 | 학교별 지표 수집 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | `/getRegionalTuitionCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | `/getRegionalScholarshipBenefitCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | `/getRegionalEducationExpensesLoanCrntSt` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 5. 한국대학교육협의회_대학알리미 재정 현황_GW | `/getRegionalEducationExpensesLoanUseStudentRatioTuition` | 지역 통계 | `regional_indicator_list` | 예 | 예 | 지역별 지표 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeByLargeSeries` | 메타데이터 | `code_list` | 예 | 예 | 학과 대계열 코드 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getUniversityMajorCode` | 학과 마스터 | `subject_list` | 예 | 예 | 학과 마스터 선행 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeByMiddleSeries` | 메타데이터 | `code_list` | 예 | 예 | 학과 중계열 코드 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeBySeriesSystem` | 메타데이터 | `raw + code_list(검토중)` | 부분 | 부분 | raw 보관 우선, 정규화 미확정 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeByPrincipalSchoolBranchSchool` | 메타데이터 | `code_list` | 예 | 예 | 본분교 코드 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeByLessonTerm` | 메타데이터 | `code_list` | 예 | 예 | 수업연한 코드 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeByDegreeCourse` | 메타데이터 | `code_list` | 예 | 예 | 학위과정 코드 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeByDayAndNight` | 메타데이터 | `code_list` | 예 | 예 | 주야간 코드 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeByCollege` | 메타데이터 | `code_list` | 예 | 예 | 단과대 코드 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeByMajorStatus` | 메타데이터 | `code_list` | 예 | 예 | 학과상태 코드 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeByMajorCharacter` | 메타데이터 | `code_list` | 예 | 예 | 학과특성 코드 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeByOneselfSeries` | 메타데이터 | `code_list` | 예 | 예 | 자체계열 코드 수집 |
| 6. 한국대학교육협의회_대학 학과 정보_GW | `/getCodeBySmallSeries` | 메타데이터 | `code_list` | 예 | 예 | 학과 소계열 코드 수집 |
| 7. 한국대학교육협의회_대학별 학과정보_GW | `/getSchoolMajorInfo` | 학과 마스터 | `subject_list` | 예 | 예 | 학교별 학과 merge |
| 8. 한국대학교육협의회_대학 및 전문대학정보_GW | `/getSchoolInfo` | 학교 마스터 | `school_list` | 예 | 예 | 학교 상세 merge |
| 9. 한국대학교육협의회_대학알리미 산학협력 현황_GW | `/getCntrctmjrInstOperCstt` | 산학협력 | `startup_support_list` | 부분 | 부분 | key-value 임시 적재 |
| 9. 한국대학교육협의회_대학알리미 산학협력 현황_GW | `/getOrdmthEdcCrseInstOper` | 산학협력 | `startup_support_list` | 부분 | 부분 | key-value 임시 적재 |
| 9. 한국대학교육협의회_대학알리미 산학협력 현황_GW | `/getGrndsPrcOperCstt` | 산학협력 | `startup_support_list` | 부분 | 부분 | key-value 임시 적재 |
| 9. 한국대학교육협의회_대학알리미 산학협력 현황_GW | `/getCsptDsgnOperCstt` | 산학협력 | `startup_support_list` | 부분 | 부분 | key-value 임시 적재 |
| 9. 한국대학교육협의회_대학알리미 산학협력 현황_GW | `/getTcherStupSuptCstt` | 산학협력 | `startup_support_list` | 부분 | 부분 | key-value 임시 적재 |
| 9. 한국대학교육협의회_대학알리미 산학협력 현황_GW | `/getStdnStupSuptCstt` | 산학협력 | `startup_support_list` | 부분 | 부분 | key-value 임시 적재 |
| 9. 한국대학교육협의회_대학알리미 산학협력 현황_GW | `/getStupEdcSuptCstt` | 산학협력 | `startup_support_list` | 부분 | 부분 | key-value 임시 적재 |

## 메모

- `sync-code-year`는 19개 메타데이터 스펙을 담당한다.
- `sync-school-master`는 학교 마스터 4개 스펙을 담당한다.
- `sync-subject-master`는 학과 마스터 2개 스펙을 담당한다.
- `sync-school-indicators`는 학교별 지표 스펙을 담당한다.
- `sync-regional-indicators`는 `getRegional*` 스펙을 담당한다.
- `sync-startup-support`는 산학협력 7개 스펙을 담당하지만, 현재 `startup_support_list` key-value 형태의 1차 적재 기준이라 상태를 `부분`으로 표기했다.
- `getCodeBySeriesSystem`은 현재 `raw` 보관 우선이라 DB 구축 상태를 `부분`으로 표기했다.
