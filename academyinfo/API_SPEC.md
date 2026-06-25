# Academyinfo API 명세 초안

## 기준

- 원천: `academyinfo/README.md`의 9개 data.go.kr OpenAPI 페이지
- 추출 방식: 각 `openapi.do` HTML에 포함된 embedded `swaggerJson` 파싱
- 목적: 후속 `DB_SCHEMA.md`, `IMPLEMENTATION_SCOPE.md` 작성용 기준 명세
- 비고: 실제 응답 샘플/운영 제약은 Swagger만으로 확정 불가한 항목이 남음

## 공통 규칙

- 모든 API는 `serviceKey`를 필수 query parameter로 사용한다.
- 응답 포맷은 Swagger 기준 `application/xml`이다.
- 공통 응답 래퍼는 대체로 `header.resultCode`, `header.resultMsg`, `body.totalCount`, `body.pageNo`, `body.numOfRows`, `body.items.item.*` 구조를 따른다.
- 페이지성 조회는 `pageNo`, `numOfRows`를 공통적으로 사용한다.

## 구현 매핑 주의사항

- 기준 점검 보고서: `academyinfo/MAPPING_GAP_REPORT.md`
- `school_list`는 `getUniversityCode` 단독 적재가 아니라 `getSchoolInfo`와 `(schl_id, svy_yr)` 기준 merge 적재가 전제다.
- `subject_list` 식별자는 `kediMjrId`보다 `schlMjrId`를 우선 사용한다.
- `BasicInformationService_1` 학과 계열 응답은 표준분류 대/중/소계열 코드·명까지 함께 저장해야 한다.
- 산학협력 7개 API는 `indctId`, `indctYr`를 공통 보존 대상으로 본다.
- 지역별 통계의 `znNmRmk`는 실응답에서 row 구분자 역할을 할 수 있어 PK/유니크키 검토 대상이다.

## API 목록 요약

| API | Host | Path 수 | 비고 |
|---|---|---:|---|
| 한국대학교육협의회_대학알리미 대학 기본 정보_GW | `apis.data.go.kr/B340014/BasicInformationService_2` | 10 | `15158963` |
| 한국대학교육협의회_대학알리미 교육여건 현황_GW | `apis.data.go.kr/B340014/EducationConditionService` | 12 | `15158679` |
| 한국대학교육협의회_대학알리미 교원·연구 현황_GW | `apis.data.go.kr/B340014/EducationResearchService` | 22 | `15158678` |
| 한국대학교육협의회 대학정보공시 학생 현황_GW | `apis.data.go.kr/B340014/StudentService` | 27 | `15158684` |
| 한국대학교육협의회_대학알리미 재정 현황_GW | `apis.data.go.kr/B340014/FinancesService` | 10 | `15158680` |
| 한국대학교육협의회_대학 학과 정보_GW | `apis.data.go.kr/B340014/BasicInformationService_1` | 13 | `15158955` |
| 한국대학교육협의회_대학별 학과정보_GW | `apis.data.go.kr/B340014/SchoolMajorInfoService` | 1 | `15158666` |
| 한국대학교육협의회_대학 및 전문대학정보_GW | `apis.data.go.kr/B340014/SchoolInfoService` | 1 | `15158665` |
| 한국대학교육협의회_대학알리미 산학협력 현황_GW | `apis.data.go.kr/B340014/IndustryAcademicCooperationService` | 7 | `15158626` |

## 1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW

- source: https://www.data.go.kr/data/15158963/openapi.do
- host: `apis.data.go.kr/B340014/BasicInformationService_2`
- schemes: https, http
- 설명: 학교유형별 코드 정보는 대학의 설립 목적과 운영 형태에 따라 대학을 체계적으로 구분·관리하기 위해 부여된 코드로 구성. 해당 코드에는 일반대학, 전문대학, 산업대학, 교육대학 등과 같이 학교의 유형을 명확하게 식별할 수 있는 정보가 포함. 이를 통해 각 유형별 대학의 특성과 기능을 구분하고 비교·분석할 수 있도록 함. 교육 통계 작성 및 정책 수립 시 기초 자료로 활용. 설립유형별 코드…

### `/getUniversityCode`

- summary: 대학 코드조회
- description: 대학 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 공시년도
 - `schlId` (optional, string) — 학교아이디
 - `schlKrnNm` (optional, string) — 학교명
 - `clgcpDivCd` (optional, string) — 본분교구분코드
 - `schlDivCd` (optional, string) — 학교구분(종류)코드
 - `znCd` (optional, string) — 지역코드
 - `estbDivCd` (optional, string) — 설립구분코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.clgcpDivCd`
 - `body.items.item.clgcpDivNm`
 - `body.items.item.estbDivCd`
 - `body.items.item.estbDivNm`
 - `body.items.item.schlDivCd`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlFullNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`
 - `body.items.item.znCd`
 - `body.items.item.znNm`
 - `body.items.item.schlKndCd`
 - `body.items.item.schlKndNm`

### `/getCodeByRegion`

- summary: 지역별 코드조회
- description: 지역별 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdnm` (optional, string) — 코드값
 - `cdid` (optional, string) — 코드아이디
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getNoticeUniversitySearchList`

- summary: 대학 검색목록_우리대학경쟁력
- description: 대학 검색목록 정보 제공 (저작권에 위배되지 않는 정보
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 공시년도
 - `schlId` (optional, string) — 학교아이디
 - `schlKrnNm` (optional, string) — 학교한글명
 - `clgcpDivCd` (optional, string) — 본분교구분코드
 - `schlDivCd` (optional, string) — 학교구분(종류)코드
 - `schlKndCd` (optional, string) — 학교유형코드
 - `znCd` (optional, string) — 지역코드
 - `estbDivCd` (optional, string) — 설립구분코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.schlId`
 - `body.items.item.clgcpDivCd`
 - `body.items.item.clgcpDivNm`
 - `body.items.item.schlDivCd`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlFullNm`
 - `body.items.item.znCd`
 - `body.items.item.znNm`
 - `body.items.item.estbDivCd`
 - `body.items.item.estbDivNm`
 - `body.items.item.schlKndCd`
 - `body.items.item.schlKndNm`
 - `body.items.item.schlKrnNm`

### `/getComparisonUniversitySearchList`

- summary: 대학 검색목록 _대학비교통계
- description: 대학 검색목록 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 공시년도
 - `schlId` (optional, string) — 학교아이디
 - `schlKrnNm` (optional, string) — 학교한글명
 - `clgcpDivCd` (optional, string) — 본분교구분코드
 - `schlDivCd` (optional, string) — 학교구분(종류)코드
 - `schlKndCd` (optional, string) — 학교유형코드
 - `znCd` (optional, string) — 지역코드
 - `estbDivCd` (optional, string) — 설립구분코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.clgcpDivCd`
 - `body.items.item.clgcpDivNm`
 - `body.items.item.schlDivCd`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlFullNm`
 - `body.items.item.znCd`
 - `body.items.item.znNm`
 - `body.items.item.estbDivCd`
 - `body.items.item.estbDivNm`
 - `body.items.item.schlKndCd`
 - `body.items.item.schlKndNm`

### `/getKeyIndicatorCode`

- summary: 주요지표 코드조회
- description: 주요지표 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `rmk` (optional, string) — 단위 ex) %, 명, 원
 - `cdnm` (optional, string) — 코드값
 - `cdid` (optional, string) — 코드아이드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`
 - `body.items.item.rmk`

### `/getComparisonPubYear`

- summary: 공시년도 조회_대학비교통계
- description: 공시년도 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.yearVal`

### `/getCodeByFound`

- summary: 설립유형별 코드조회
- description: 설립유형별 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdid` (optional, string) — 코드아이디
 - `cdnm` (optional, string) — 코드값
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getNoticeSvyYear`

- summary: 조사년도 조회_우리대학경쟁력
- description: 조사년도 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.yearVal`

### `/getCodeByType`

- summary: 학교유형별코드조회
- description: 학교유형별코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdnm` (optional, string) — 코드값
 - `cdid` (optional, string) — 코드아이디
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getCodeByKind`

- summary: 학교종류별 코드조회
- description: 학교종류별 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdnm` (optional, string) — 코드값
 - `cdid` (optional, string) — 코드아이디
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

## 2. 한국대학교육협의회_대학알리미 교육여건 현황_GW

- source: https://www.data.go.kr/data/15158679/openapi.do
- host: `apis.data.go.kr/B340014/EducationConditionService`
- schemes: https, http
- 설명: 본 데이터는 한국대학교육협의회에서 운영하는 대학알리미를 기반으로 수집된 것으로, 국내 대학의 교육여건 현황을 종합적으로 제공.. 주요 항목으로는 대학의 물리적 및 재정적 교육 인프라 수준을 파악할 수 있는 지표들이 포함되어 있으며, 구체적으로 교지 및 교사 확보율, 기숙사 수용 현황, 수익용 기본재산 확보율, 학생 1인당 자료 구입비 등이 제공. 교지·교사 확보율은 …

### `/getComparisonLibraryBudgetCrntSt`

- summary: 도서관예산 현황 조회_대학비교통계
- description: 도서관예산 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`
 - `body.items.item.indctVal1`

### `/getComparisonDormitoryAcceptanceCrntSt`

- summary: 기숙사 수용 현황 조회_대학비교통계
- description: 기숙사 수용 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.totalCount`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getComparisonBasicPropertiesForProfitBurdenRate`

- summary: 수익용 기본재산 부담률_대학비교통계
- description: 공시년도,학교아이디를 기준으로 학교종류, 설립구분, 수익용 기본재산 부담률등을 제공하는 수익용 기본재산 부담률 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getComparisonBasicPropertiesForprofitCrntSt`

- summary: 수익용기본재산 확보 현황 조회_대학비교통계
- description: 수익용기본재산 확보 현황 정보 제공 (저작권에 위배되지 않는 정보
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getComparisonStudentForPersonDataPurchasePrice`

- summary: 학생 1인당 자료 구입비_대학비교통계
- description: 공시년도,학교아이디를 기준으로 학교종류, 설립구분, 학생 1인당 자료 구입비등을 제공하는 학생 1인당 자료 구입비 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getComparisonSchoolGroundsAndBdsEnsureRate`

- summary: 교지, 교사 확보율 조회_대학비교통계
- description: 교지, 교사 확보율 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `indctId` (optional, string) — 지표아이디
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.numOfRows`
 - `body.totalCount`
 - `body.pageNo`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`

### `/getRegionalSchoolGroundsAndBdsEnsureRate`

- summary: 교지, 교사 확보율 조회_지역별통계
- description: 교지·교사 확보율 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `indctId` (optional, string) — 지표아이디
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getRegionalDormitoryAcceptanceCrntSt`

- summary: 기숙사 수용 현황 조회_지역별통계
- description: 기숙사 수용 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getRegionalLibraryBudgetCrntSt`

- summary: 도서관예산 현황 조회_지역별통계
- description: 도서관예산 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getRegionalBasicPropertiesForProfitBurdenRate`

- summary: 수익용 기본재산 부담률_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 수익용 기본재산 부담률 등을 제공하는 수익용 기본재산 부담률 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.schlDivCd`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`

### `/getRegionalBasicPropertiesForprofitCrntSt`

- summary: 수익용기본재산 확보 현황 조회_지역별통계
- description: 수익용기본재산 확보 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getRegionalStudentForPersonDataPurchasePrice`

- summary: 학생 1인당 자료 구입비_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 학생 1인당 자료 구입비 등을 제공하는 학생 1인당 자료 구입비 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

## 3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW

- source: https://www.data.go.kr/data/15158678/openapi.do
- host: `apis.data.go.kr/B340014/EducationResearchService`
- schemes: https, http
- 설명: 전임교원 확보율, 전임교원 1인당 학생수, 전임교원 1인당 연구비, 전임교원 1인당 저·역서 수, 전임교원 강의 담당 비율, 비전임교원 강의 담당 비율, 외국인 전임교원 현황 등 대학의 교육 및 연구 역량을 종합적으로 파악할 수 있는 다양한 지표를 포함하며, 이를 통해 교원 구성의 질적 수준과 강의 운영 구조, 연구 성과, 교육의 안정성 및 효율성, 그리고 국제화 수준 등을 다각도로 분석할 …

### `/getComparisonGypsyScholarFacultyLectureChargeRatio`

- summary: 비전임교원 강의담당비율_대학비교통계
- description: 공시년도, 학교아이디를 기준으로 학교종류, 설립구분, 비전임교원 강의담당비율 등을 제공하는 비전임교원 강의담당비율 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalGypsyScholarFacultyLectureChargeRatio`

- summary: 비전임교원 강의담당비율_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 비전임교원 강의담당비율 등을 제공하는 비전임교원 강의담당비율 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonForeignFullTimeFacultyCrntSt`

- summary: 외국인 전임교원 현황 조회_대학비교통계
- description: 외국인 전임교원 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalForeignFullTimeFacultyCrntSt`

- summary: 외국인 전임교원 현황 조회_지역별통계
- description: 외국인 전임교원 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonFullTimeFacultyForPersonBookTranslatedBook`

- summary: 전임교원 1인당 저역서_대학비교통계
- description: 공시년도, 학교아이디를 기준으로 학교종류, 설립구분, 전임교원 1인당 저역서등을 제공하는 전임교원 1인당 저역서 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — [대학정보공시 코드조회 > 대학 코드조회 API]로 schlId 확인 가능
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalFullTimeFacultyForPersonBookTranslatedBook`

- summary: 전임교원 1인당 저역서_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 전임교원 1인당 저역서 등을 제공하는 전임교원 1인당 저역서 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonFullTimeFacultyForPersonStudentNumberEnrolledStudent`

- summary: 전임교원 1인당 학생수(재학생)_대학비교통계
- description: 공시년도,학교아이디를 기준으로 학교종류, 설립구분, 전임교원 1인당 학생수(재학생) 등을 제공하는 전임교원 1인당 학생수(재학생) 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — [대학정보공시 코드조회 > 대학 코드조회 API]로 schlId 확인 가능
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalFullTimeFacultyForPersonStudentNumberEnrolledStudent`

- summary: 전임교원 1인당 학생수(재학생)_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 전임교원 1인당 학생수(재학생)등을 제공하는 전임교원 1인당 학생수(재학생) 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonFullTimeFacultyForPersonStudentNumberFixedNumber`

- summary: 전임교원 1인당 학생수(편제정원기준)_대학비교통계
- description: 공시년도,학교아이디를 기준으로 학교종류, 설립구분, 전임교원 1인당 학생수(편제정원기준) 등을 제공하는 전임교원 1인당 학생수(편제정원기준) 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalFullTimeFacultyForPersonStudentNumberFixedNumber`

- summary: 전임교원 1인당 학생수(편제정원기준)_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 전임교원 1인당 학생수(편제정원기준) 등을 제공하는 전임교원 1인당 학생수(편제정원기준) 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonLectureChargeRatio`

- summary: 전임교원 강의담당비율 조회_대학비교통계
- description: 강의담당비율 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (optional, string) — 학교아이디
 - `svyYr` (optional, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalLectureChargeRatio`

- summary: 전임교원 강의담당비율 조회_지역별통계
- description: 강의담당비율 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonFullTimeFacultyInsideOfSchoolForPersonResearchGrant`

- summary: 전임교원 교내 1인당 연구비_대학비교통계
- description: 공시년도,학교아이디를 기준으로 학교종류, 설립구분, 전임교원 교내 1인당 연구비 등을 제공하는 전임교원 교내 1인당 연구비 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalFullTimeFacultyInsideOfSchoolForPersonResearchGrant`

- summary: 전임교원 교내 1인당 연구비_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 전임교원 교내 1인당 연구비 등을 제공하는 전임교원 교내 1인당 연구비 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonFullTimeFacultyOutsideOfSchoolForPersonResearchGrant`

- summary: 전임교원 교외 1인당 연구비_대학비교통계
- description: 공시년도, 학교아이디를 기준으로 학교종류, 설립구분, 전임교원 교외 1인당 연구비 등을 제공하는 전임교원 교외 1인당 연구비 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalFullTimeFacultyOutsideOfSchoolForPersonResearchGrant`

- summary: 전임교원 교외 1인당 연구비_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 전임교원 교외 1인당 연구비등을 제공하는 전임교원 교외 1인당 연구비 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonFullTimeFacultyResearchCrntSt`

- summary: 전임교원 연구 실적 현황 조회_대학비교통계
- description: 전임교원 연구 실적 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 공시년도
 - `schlId` (required, string) — 학교아이디
 - `indctId` (required, string) — 지표아이디
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getNoticeFullTimeFacultyResearchCrntSt`

- summary: 전임교원 연구 실적 현황 조회_우리대학경쟁력
- description: 전임교원 연구 실적 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 공시년도
 - `schlId` (required, string) — 학교아이디
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal4`
 - `body.items.item.indctAvg`
 - `body.items.item.indctImg`
 - `body.items.item.svyYr`
 - `body.items.item.indctId`
 - `body.items.item.indctVal3`

### `/getRegionalFullTimeFacultyResearchCrntSt`

- summary: 전임교원 연구 실적 현황 조회_지역별통계
- description: 전임교원 연구 실적 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`
 - `body.items.item.fieldType7`

### `/getComparisonFullTimeFacultyEnsureCrntSt`

- summary: 전임교원 확보 현황 조회_대학비교통계
- description: 전임교원 확보 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `indctId` (required, string) — 지표아이디
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalFullTimeFacultyEnsureCrntSt`

- summary: 전임교원 확보 현황 조회_지역별통계
- description: 전임교원 확보 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `indctId` (optional, string) — 지표아이디
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getNoticeFullTimeFacultyEnsureRate`

- summary: 전임교원확보율 조회_우리대학경쟁력
- description: 전임교원확보율 정보 제공(저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 공시년도
 - `schlId` (required, string) — 학교아이디
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal3`
 - `body.items.item.indctVal4`
 - `body.items.item.indctAvg`
 - `body.items.item.indctImg`
 - `body.items.item.svyYr`
 - `body.items.item.indctId`

## 4. 한국대학교육협의회 대학정보공시 학생 현황_GW

- source: https://www.data.go.kr/data/15158684/openapi.do
- host: `apis.data.go.kr/B340014/StudentService`
- schemes: https, http
- 설명: 본 데이터는 한국대학교육협의회에서 운영하는 대학알리미를 기반으로 수집된 것으로, 국내 대학의 입학, 재학, 졸업 및 학생 성과 전반에 대한 현황을 종합적으로 제공. 주요 항목으로는 대학의 학생 선발 구조와 학사 운영 성과를 파악할 수 있는 지표들이 포함되어 있으며, 구체적으로 신입생 기회균형선발 비율, 신입생 충원율, 외국인 학생 수 및 외국인 중도탈락 학생 수, 입학전형 최종 등록률,…

### `/getComparisonFreshmanChanceBalanceSelectionRatio`

- summary: 신입생 기회균형 선발 비율_대학비교통계
- description: 공시년도,학교아이디를 기준으로 학교종류, 설립구분, 신입생 기회균형 선발 비율 등을 제공하는 신입생 기회균형 선발 비율 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalFreshmanChanceBalanceSelectionRatio`

- summary: 신입생 기회균형 선발 비율_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 신입생 기회균형 선발 비율 등을 제공하는 신입생 기회균형 선발 비율 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonFreshmanEnsureCrntSt`

- summary: 신입생 충원 현황 조회_대학비교통계
- description: 신입생 충원 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalFreshmanEnsureCrntSt`

- summary: 신입생 충원 현황 조회_지역별통계
- description: 신입생 충원 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getNoticeFreshmanDrafteesRate`

- summary: 신입생 충원율 조회_우리대학경쟁력
- description: 신입생충원율 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 공시년도
 - `schlId` (required, string) — 학교아이디
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal4`
 - `body.items.item.indctAvg`
 - `body.items.item.indctImg`
 - `body.items.item.svyYr`
 - `body.items.item.indctId`

### `/getComparisonForeignDropOutCrntSt`

- summary: 외국인 중도탈락 학생 현황 조회_대학비교통계
- description: 외국인 중도탈락 학생 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalForeignDropOutCrntSt`

- summary: 외국인 중도탈락 학생 현황 조회_지역별통계
- description: 외국인 중도탈락 학생 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonForeignStudentCrntSt`

- summary: 외국인 학생 현황 조회_대학비교통계
- description: 외국인 학생 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalForeignStudentCrntSt`

- summary: 외국인 학생 현황 조회_지역별통계
- description: 외국인 학생 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonEntranceModelLastRegistrationRatio`

- summary: 입학전형 최종 등록률_대학비교통계
- description: 공시년도, 학교아이디등을 기준으로 학교종류, 설립구분, 입학전형 최종 등록률등을 제공하는 입학전형 최종 등록률 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalEntranceModelLastRegistrationRatio`

- summary: 입학전형 최종 등록률_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 입학전형 최종 등록률 등을 제공하는 입학전형 최종 등록률 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonEnrolledStudentCrntSt`

- summary: 재적학생 현황 조회_대학비교통계
- description: 재적학생 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalEnrolledStudentCrntSt`

- summary: 재적학생 현황 조회_지역별통계
- description: 재적학생 현황 조회 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getNoticeEnrolledStudentDrafteesRate`

- summary: 재학생 충원율 조회_우리대학경쟁력
- description: 재학생충원율 정보 제공(저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 공시년도
 - `schlId` (required, string) — 학교아이디
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal3`
 - `body.items.item.indctVal4`
 - `body.items.item.indctAvg`
 - `body.items.item.indctImg`
 - `body.items.item.svyYr`
 - `body.items.item.indctId`

### `/getComparisonEnrolledStudentEnsureRate`

- summary: 재학생 충원율_대학비교통계
- description: 공시년도,학교아이디를 기준으로 학교종류, 설립구분, 재학생 충원율 등을 제공하는 재학생 충원율 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalEnrolledStudentEnsureRate`

- summary: 재학생 충원율_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 재학생 충원율 등을 제공하는 재학생 충원율 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonEnrolledStudent`

- summary: 재학생_대학비교통계
- description: 공시년도,학교아이디를 기준으로 학교종류, 설립구분, 재학생 수 등을 제공하는 재학생 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalEnrolledStudent`

- summary: 재학생_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 재학생수 등을 제공하는 재학생 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonInsideFixedNumberFreshmanCompetitionRate`

- summary: 정원내 신입생 경쟁률_대학비교통계
- description: 공시년도, 학교아이디를 기준으로 학교종류, 설립구분, 정원내 신입생 경쟁률 등을 제공하는 정원내 신입생 경쟁률 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — [대학정보공시 코드조회 > 대학 코드조회 API]로 schlId 확인 가능
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalInsideFixedNumberFreshmanCompetitionRate`

- summary: 정원내 신입생 경쟁률_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 정원내 신입생 경쟁률 등을 제공하는 정원내 신입생 경쟁률 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getRegionalGraduateEnterFindJobCrntSt`

- summary: 졸업생의 진학, 취업 현황 정보 조회_지역별통계
- description: 졸업생의 진학, 취업 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `indctId` (optional, string) — 지표아이디
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getNoticeGraduateEmploymentRate`

- summary: 졸업생의 취업현황 조회_우리대학경쟁력
- description: 졸업생취업율 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 공시년도
 - `schlId` (required, string) — 학교아이디
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal3`
 - `body.items.item.indctVal4`
 - `body.items.item.indctAvg`
 - `body.items.item.indctImg`
 - `body.items.item.svyYr`
 - `body.items.item.apyYr`
 - `body.items.item.indctId`

### `/getComparisonDropOutStudentCrntSt`

- summary: 중도탈락 학생 현황 조회_대학비교통계
- description: 중도탈락 학생 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalDropOutStudentCrntSt`

- summary: 중도탈락 학생 현황 조회_지역별통계
- description: 중도탈락 학생 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getNoticeStudentsWastageRate`

- summary: 중도탈락 학생비율 조회_우리대학경쟁력
- description: 중도탈락 학생비율 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal4`
 - `body.items.item.indctAvg`
 - `body.items.item.indctImg`
 - `body.items.item.svyYr`
 - `body.items.item.indctId`

### `/getComparisonStudentOnALeaveOfAbsence`

- summary: 휴학생_대학비교통계
- description: 공시년도, 학교아이디를 기준으로 학교종류, 설립구분, 휴학생 수 등을 제공하는 휴학생 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalStudentOnALeaveOfAbsence`

- summary: 휴학생_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 휴학생수 등을 제공하는 휴학생 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

## 5. 한국대학교육협의회_대학알리미 재정 현황_GW

- source: https://www.data.go.kr/data/15158680/openapi.do
- host: `apis.data.go.kr/B340014/FinancesService`
- schemes: https, http
- 설명: 본 데이터는 한국대학교육협의회에서 운영하는 대학알리미를 기반으로 수집된 것으로, 국내 대학의 등록금 및 학생 재정 지원 현황을 종합적으로 제공. 주요 항목으로는 등록금 수준과 학생 재정 지원 및 교육 투자 규모를 파악할 수 있는 지표들이 포함되어 있으며, 구체적으로 등록금 현황, 장학금 수혜 현황, 학자금 대출 학생 수, 학생 1인당 교육(투자)비 등이 제공. 등록금 현황은 대학별…

### `/getComparisonTuitionCrntSt`

- summary: 등록금 현황 조회_대학비교통계
- description: 등록금 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getComparisonScholarshipBenefitCrntSt`

- summary: 장학금 수혜 현황 조회_대학비교통계
- description: 장학금 수혜 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getComparisonEducationalExpensesReductionCrntSt`

- summary: 학생 1인당 교육비 환원 현황 조회_대학비교통계
- description: 학생 1인당 교육비 환원 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `indctId` (optional, string) — 지표아이디
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalEducationalExpensesReductionCrntSt`

- summary: 학생 1인당 교육비 환원 현황 조회_지역별통계
- description: 학생 1인당 교육비 환원 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `indctId` (optional, string) — 지표아이디
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getComparisonEducationExpensesLoanCrntSt`

- summary: 학자금 대출 현황 조회_대학비교통계
- description: 학자금 대출 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getComparisonEducationExpensesLoanUseStudentRatioTuition`

- summary: 학자금대출 이용학생비율(등록금(학비))_대학비교통계
- description: 공시년도,학교아이디를 기준으로 학교종류, 설립구분, 학자금대출 이용학생비율(등록금(학비)) 등을 제공하는 학자금대출 이용학생비율(등록금(학비)) 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlId` (required, string) — 학교아이디
 - `svyYr` (required, string) — 공시년도
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctId`
 - `body.items.item.indctVal1`
 - `body.items.item.indctYr`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.schlId`
 - `body.items.item.schlKrnNm`
 - `body.items.item.svyYr`

### `/getRegionalTuitionCrntSt`

- summary: 등록금 현황 조회_지역별통계
- description: 등록금 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getRegionalScholarshipBenefitCrntSt`

- summary: 장학금 수혜 현황 조회_지역별통계
- description: 장학금 수혜 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getRegionalEducationExpensesLoanCrntSt`

- summary: 학자금 대출 현황 조회_지역별통계
- description: 학자금 대출 현황 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (required, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.fieldType1`
 - `body.items.item.fieldType2`
 - `body.items.item.fieldType3`
 - `body.items.item.fieldType4`
 - `body.items.item.fieldType5`
 - `body.items.item.fieldType6`
 - `body.items.item.fieldType7`
 - `body.items.item.fieldVal1`
 - `body.items.item.fieldVal2`
 - `body.items.item.fieldVal3`
 - `body.items.item.fieldVal4`
 - `body.items.item.fieldVal5`
 - `body.items.item.fieldVal6`
 - `body.items.item.fieldVal7`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

### `/getRegionalEducationExpensesLoanUseStudentRatioTuition`

- summary: 학자금대출 이용학생비율(등록금(학비))_지역별통계
- description: 학교구분을 기준으로 학교구분, 지역 이름, 학자금대출 이용학생비율(등록금(학비)) 등을 제공하는 학자금대출 이용학생비율(등록금(학비)) 조회 서비스
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `schlDivCd` (optional, string) — 학교구분
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.indctFirstSchlCntRmk`
 - `body.items.item.indctSecondSchlCntRmk`
 - `body.items.item.indctThirdSchlCntRmk`
 - `body.items.item.indctFirstSvyYr`
 - `body.items.item.indctSecondSvyYr`
 - `body.items.item.indctThirdSvyYr`
 - `body.items.item.znNmRmk`
 - `body.items.item.indctFirstSchlCnt`
 - `body.items.item.indctSecondSchlCnt`
 - `body.items.item.indctThirdSchlCnt`
 - `body.items.item.indctFirstVal`
 - `body.items.item.indctSecondVal`
 - `body.items.item.indctThirdVal`
 - `body.items.item.znNm`
 - `body.items.item.indctId`
 - `body.items.item.schlDivCd`

## 6. 한국대학교육협의회_대학 학과 정보_GW

- source: https://www.data.go.kr/data/15158955/openapi.do
- host: `apis.data.go.kr/B340014/BasicInformationService_1`
- schemes: https, http
- 설명: 교육관련기관의 정보공개에 관한 특례법 및 동법 시행령을 근거로, 한국대학교육협의회에서 대학 학과 정보를 체계적으로 수집·정리. 대학 학과 정보에는 학과 명칭, 전공 분야, 모집 단위, 입학 정원, 교육과정 특성 등의 세부 내용이 포함. 학교별 학과정보는 각 대학이 보유한 학과의 구성, 운영 현황, 특성을 파악하고 상호 비교할 수 있도록 제공. 지역별 학과정보는 특정 지역 내 대학들의 학과 분…

### `/getCodeByLargeSeries`

- summary: 표준분류 대계열 코드조회
- description: 표준분류 대계열 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사년도
 - `cdid` (optional, string) — 표준분류 대계열 코드
 - `cdnm` (optional, string) — 표준분류 대계열 코드명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getUniversityMajorCode`

- summary: 학교별학과 코드조회
- description: 학교별학과 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사년도
 - `schlId` (required, string) — 학교ID
 - `schlMjrId` (optional, string) — 학교학과ID
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.srsSclftCd`
 - `body.items.item.srsMclftCd`
 - `body.items.item.srsLclftCd`
 - `body.items.item.schlMjrStatNm`
 - `body.items.item.schlMjrStatCd`
 - `body.items.item.schlMjrId`
 - `body.items.item.schlMjrCharNm`
 - `body.items.item.schlMjrCharCd`
 - `body.items.item.schlKndNm`
 - `body.items.item.schlKndCd`
 - `body.items.item.schlId`
 - `body.items.item.schlEstbDivNm`
 - `body.items.item.schlEstbDivCd`
 - `body.items.item.psbsDivNm`
 - `body.items.item.psbsDivCd`
 - `body.items.item.pbnfDgriCrseDivNm`
 - `body.items.item.pbnfDgriCrseDivCd`
 - `body.items.item.onsfSrsClftNm`
 - `body.items.item.onsfSrsClftCd`
 - `body.items.item.mjrUpdtDtm`
 - `body.items.item.mjrId`
 - `body.items.item.mjrAreaSignguNm`
 - `body.items.item.mjrAreaNm`
 - `body.items.item.mjrAreaCd`
 - `body.items.item.lsnTrmNm`
 - `body.items.item.lsnTrmCd`
 - `body.items.item.korSrsSclftNm`
 - `body.items.item.korSrsMclftNm`
 - `body.items.item.korSrsLclftNm`
 - `body.items.item.korSchlNm`
 - `body.items.item.korMjrNm`
 - `body.items.item.kediMjrId`
 - `body.items.item.grdtNum`
 - `body.items.item.eschlPscpNum`
 - `...` (8개 추가 필드)

### `/getCodeByMiddleSeries`

- summary: 표준분류 중계열 코드조회
- description: 표준분류 중계열 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사년도
 - `cdid` (optional, string) — 표준분류 중계열 코드
 - `cdnm` (optional, string) — 표준분류 중계열 코드명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getCodeBySeriesSystem`

- summary: 표준분류 계열체계 조회
- description: 표준분류 계열체계 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사년도
 - `srsLclftCd` (optional, string) — 표준분류 대계열 코드
 - `srsMclftCd` (optional, string) — 표준분류 중계열 코드
 - `srsSclftCd` (optional, string) — 표준분류 소계열 코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.srsLclftCd`
 - `body.items.item.srsMclftCd`
 - `body.items.item.srsSclftCd`

### `/getCodeByPrincipalSchoolBranchSchool`

- summary: 본분교 코드조회
- description: 본분교 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdid` (optional, string) — 본분교구분코드
 - `cdnm` (optional, string) — 본분교구분명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getCodeByLessonTerm`

- summary: 수업연한 코드조회
- description: 수업연한 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdid` (optional, string) — 수업연한코드
 - `cdnm` (optional, string) — 수업연한명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getCodeByDegreeCourse`

- summary: 학위과정 코드조회
- description: 학위과정 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdid` (optional, string) — 공시학위과정구분코드
 - `cdnm` (optional, string) — 공시학위과정구분명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getCodeByDayAndNight`

- summary: 주야간 코드조회
- description: 주야간 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdid` (optional, string) — 주야간구분코드
 - `cdnm` (optional, string) — 주야간구분명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getCodeByCollege`

- summary: 단과대학 코드조회
- description: 단과대학 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdid` (optional, string) — 단과대학코드
 - `cdnm` (optional, string) — 단과대학명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getCodeByMajorStatus`

- summary: 학과상태 코드조회
- description: 학과상태 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdid` (optional, string) — 학교학과상태코드
 - `cdnm` (optional, string) — 학교학과상태명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getCodeByMajorCharacter`

- summary: 학과특성 코드조회
- description: 학과특성 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdid` (optional, string) — 학교학과특성코드
 - `cdnm` (optional, string) — 학교학과특성명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getCodeByOneselfSeries`

- summary: 대학자체계열 코드조회
- description: 대학자체계열 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `cdid` (optional, string) — 자체계열분류코드
 - `cdnm` (optional, string) — 자체계열분류명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

### `/getCodeBySmallSeries`

- summary: 표준분류 소계열 코드조회
- description: 표준분류 소계열 코드 정보 제공 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사년도
 - `cdid` (optional, string) — 표준분류 소계열 코드
 - `cdnm` (optional, string) — 표준분류 소계열 코드명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.cdid`
 - `body.items.item.cdnm`

## 7. 한국대학교육협의회_대학별 학과정보_GW

- source: https://www.data.go.kr/data/15158666/openapi.do
- host: `apis.data.go.kr/B340014/SchoolMajorInfoService`
- schemes: https, http
- 설명: 표준데이터셋으로 제공하는 ‘한국대학교육협의회_대학별 학과정보’를 API로 제공하며, 대학별 개설 학과에 대한 기본 정보와 함께 학과특성, 수업연한, 학위과정(학사·석사·박사 등), 교육목표, 개설 여부, 계열 및 전공 구분, 입학정원 등 다양한 세부 항목을 포함하여 조회할 수 있도록 구성. 또한 최신 데이터를 기반으로 지속적인 업데이트를 지원하여 정보의 정확성과 신뢰성을 확보하고, 진로 탐색…

### `/getSchoolMajorInfo`

- summary: 한국대학교육협의회_대학별 학과정보
- description: 한국대학교육협의회_대학별 학과정보(저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사년도
 - `schlId` (optional, string) — 학교코드
 - `schlKrnNm` (required, string) — 학교명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.clgNm`
 - `body.items.item.dghtDivNm`
 - `body.items.item.edcCrseLtrCtnt`
 - `body.items.item.eschlPscpNum`
 - `body.items.item.grdtNum`
 - `body.items.item.kediMjrId`
 - `body.items.item.korMjrNm`
 - `body.items.item.lsnTrmNm`
 - `body.items.item.lstUpdtDtm`
 - `body.items.item.mjrAreaCd`
 - `body.items.item.mjrAreaNm`
 - `body.items.item.mjrAreaSignguCd`
 - `body.items.item.mjrAreaSignguNm`
 - `body.items.item.mjrUpdtDtm`
 - `body.items.item.onsfSrsClftNm`
 - `body.items.item.pbnfDgriCrseDivNm`
 - `body.items.item.pwayEmplLtrCtnt`
 - `body.items.item.schlKndNm`
 - `body.items.item.schlMjrCharNm`
 - `body.items.item.schlMjrStatNm`
 - `body.items.item.schlNm`
 - `body.items.item.stdClftMjrId`
 - `body.items.item.svyYr`

## 8. 한국대학교육협의회_대학 및 전문대학정보_GW

- source: https://www.data.go.kr/data/15158665/openapi.do
- host: `apis.data.go.kr/B340014/SchoolInfoService`
- schemes: https, http
- 설명: 표준데이터셋으로 제공하는 '한국대학교육협의회_대학 및 전문대학정보'를 API로 제공, 대학 및 전문대학의 학교구분, 설립형태, 소재지 등의 정보를 포함하여 학제 구분, 운영 형태, 설립 주체, 지역별 분포, 학교 유형별 특성, 규모 및 기본 현황 등 다양한 세부 정보를 함께 제공하며, 교육기관 현황을 체계적으로 파악하고 분석·활용할 수 있도록 지원하고, 관련 서비스 개발 및 정책 수립, 연…

### `/getSchoolInfo`

- summary: 한국대학교육협의회_대학 및 전문대학정보
- description: 한국대학교육협의회 대학 및 전문대학정보 제공(저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사년도
 - `schlId` (optional, string) — 학교코드
 - `schlKrnNm` (required, string) — 학교명
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.lstUpdtDtm`
 - `body.items.item.pbnfAreaCd`
 - `body.items.item.pbnfAreaNm`
 - `body.items.item.postNo`
 - `body.items.item.postNoAdrs`
 - `body.items.item.psbsDivNm`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEngNm`
 - `body.items.item.schlEstbDivNm`
 - `body.items.item.schlEstbDt`
 - `body.items.item.schlId`
 - `body.items.item.schlKndNm`
 - `body.items.item.schlNm`
 - `body.items.item.schlRepFxNoCtnt`
 - `body.items.item.schlRepTpNoCtnt`
 - `body.items.item.schlUrlAdrs`
 - `body.items.item.svyYr`

## 9. 한국대학교육협의회_대학알리미 산학협력 현황_GW

- source: https://www.data.go.kr/data/15158626/openapi.do
- host: `apis.data.go.kr/B340014/IndustryAcademicCooperationService`
- schemes: https, http
- 설명: 대학공시정보에서 사용되는 산학협력 공시정보(저작권에 위배되지 않는 정보), 현장실습운영현황, 캡스톤디자인운영현황, 계약학과설치운영현황, 주문식교육과정설치운영현황, 교원의창업및창업지원현황, 학생의창업및창업지원현황, 창업교육지원현황, 산학공동연구실적현황, 기술이전및사업화성과현황, 산학협력단운영현황, 산업체참여교과목운영현황, 취업연계프로그램운영현황, 창업보육센터운영현황, 창업동아리운영현황, 산학협…

### `/getCntrctmjrInstOperCstt`

- summary: 계약학과설치운영현황
- description: 대학공시정보에서 사용되는 사회맞춤형 교육과정 계약학과 설치 운영 현황 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사연도(공시연도)
 - `schlId` (required, string) — 학교코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.schlKrnNm`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal3`
 - `body.items.item.indctVal4`
 - `body.items.item.indctVal5`
 - `body.items.item.indctVal6`
 - `body.items.item.indctVal7`
 - `body.items.item.indctVal8`
 - `body.items.item.indctVal9`
 - `body.items.item.indctVal10`
 - `body.items.item.indctVal11`
 - `body.items.item.indctVal12`
 - `body.items.item.indctVal13`
 - `body.items.item.indctVal14`
 - `body.items.item.indctVal15`
 - `body.items.item.indctVal16`
 - `body.items.item.indctVal17`
 - `body.items.item.indctVal18`
 - `body.items.item.indctVal19`
 - `body.items.item.indctVal20`
 - `body.items.item.indctVal21`
 - `body.items.item.indctVal22`
 - `body.items.item.indctVal23`
 - `body.items.item.indctVal24`
 - `body.items.item.indctVal25`
 - `body.items.item.indctId`
 - `body.items.item.schlId`
 - `body.items.item.indctYr`

### `/getOrdmthEdcCrseInstOper`

- summary: 주문식교육과정설치운영현황
- description: 대학공시정보에서 사용되는 사회맞춤형 교육과정 주문식 교육과정 설치 운영 현황 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사연도(공시연도)
 - `schlId` (required, string) — 학교코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.schlKrnNm`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal3`
 - `body.items.item.indctVal4`
 - `body.items.item.indctVal5`
 - `body.items.item.indctVal6`
 - `body.items.item.indctVal7`
 - `body.items.item.indctVal8`
 - `body.items.item.indctVal9`
 - `body.items.item.indctVal10`
 - `body.items.item.indctVal11`
 - `body.items.item.indctVal12`
 - `body.items.item.indctVal13`
 - `body.items.item.indctVal14`
 - `body.items.item.indctVal15`
 - `body.items.item.indctVal16`
 - `body.items.item.indctVal17`
 - `body.items.item.indctVal18`
 - `body.items.item.indctVal19`
 - `body.items.item.indctId`
 - `body.items.item.schlId`
 - `body.items.item.indctYr`

### `/getGrndsPrcOperCstt`

- summary: 현장실습운영현황
- description: 대학공시정보에서 사용되는 대학별 현장실습 운영 현황 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사연도(공시연도)
 - `schlId` (required, string) — 학교코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.schlKrnNm`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal3`
 - `body.items.item.indctVal4`
 - `body.items.item.indctVal5`
 - `body.items.item.indctVal6`
 - `body.items.item.indctVal7`
 - `body.items.item.indctVal8`
 - `body.items.item.indctVal9`
 - `body.items.item.indctVal10`
 - `body.items.item.indctVal11`
 - `body.items.item.indctVal12`
 - `body.items.item.indctVal13`
 - `body.items.item.indctVal14`
 - `body.items.item.indctVal15`
 - `body.items.item.indctVal16`
 - `body.items.item.indctVal17`
 - `body.items.item.indctId`
 - `body.items.item.schlId`
 - `body.items.item.indctYr`

### `/getCsptDsgnOperCstt`

- summary: 캡스톤디자인운영현황
- description: 대학공시정보에서 사용되는 캡스톤 디자인 운영 현황(저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사연도(공시연도)
 - `schlId` (required, string) — 학교코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.schlKrnNm`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal3`
 - `body.items.item.indctVal4`
 - `body.items.item.indctVal5`
 - `body.items.item.indctVal6`
 - `body.items.item.indctVal7`
 - `body.items.item.indctVal8`
 - `body.items.item.indctVal9`
 - `body.items.item.indctVal10`
 - `body.items.item.indctVal11`
 - `body.items.item.indctVal12`
 - `body.items.item.indctVal13`
 - `body.items.item.indctVal14`
 - `body.items.item.indctVal15`
 - `body.items.item.indctVal16`
 - `body.items.item.indctVal17`
 - `body.items.item.indctId`
 - `body.items.item.schlId`
 - `body.items.item.indctYr`

### `/getTcherStupSuptCstt`

- summary: 교원의창업및창업지원현황
- description: 대학공시정보에서 사용되는 교원의 창업 및 창업지원 현황 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사연도(공시연도)
 - `schlId` (required, string) — 학교코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.schlKrnNm`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal3`
 - `body.items.item.indctVal4`
 - `body.items.item.indctVal5`
 - `body.items.item.indctVal6`
 - `body.items.item.indctVal7`
 - `body.items.item.indctVal8`
 - `body.items.item.indctVal9`
 - `body.items.item.indctVal10`
 - `body.items.item.indctVal11`
 - `body.items.item.indctVal12`
 - `body.items.item.indctId`
 - `body.items.item.schlId`
 - `body.items.item.indctYr`

### `/getStdnStupSuptCstt`

- summary: 학생의창업및창업지원현황
- description: 대학공시정보에서 사용되는 학생의 창업 및 창업지원 현황 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사연도(공시연도)
 - `schlId` (required, string) — 학교코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.schlKrnNm`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal3`
 - `body.items.item.indctVal4`
 - `body.items.item.indctVal5`
 - `body.items.item.indctVal6`
 - `body.items.item.indctVal7`
 - `body.items.item.indctVal8`
 - `body.items.item.indctVal9`
 - `body.items.item.indctVal10`
 - `body.items.item.indctVal11`
 - `body.items.item.indctVal12`
 - `body.items.item.indctId`
 - `body.items.item.schlId`
 - `body.items.item.indctYr`

### `/getStupEdcSuptCstt`

- summary: 창업교육지원현황
- description: 대학공시정보에서 사용되는 학생의 창업 및 창업지원 현황 (저작권에 위배되지 않는 정보)
- query parameters:
 - `serviceKey` (required, string) — 공공데이터포털에서 받은 인증키
 - `pageNo` (optional, string) — 페이지번호
 - `numOfRows` (optional, string) — 한 페이지 결과 수
 - `svyYr` (required, string) — 조사연도(공시연도)
 - `schlId` (required, string) — 학교코드
- response 핵심 필드:
 - `header.resultCode`
 - `header.resultMsg`
 - `body.totalCount`
 - `body.pageNo`
 - `body.numOfRows`
 - `body.items.item.svyYr`
 - `body.items.item.schlKrnNm`
 - `body.items.item.schlDivNm`
 - `body.items.item.schlEstbNm`
 - `body.items.item.indctVal1`
 - `body.items.item.indctVal2`
 - `body.items.item.indctVal3`
 - `body.items.item.indctVal4`
 - `body.items.item.indctVal5`
 - `body.items.item.indctVal6`
 - `body.items.item.indctVal7`
 - `body.items.item.indctVal8`
 - `body.items.item.indctVal9`
 - `body.items.item.indctVal10`
 - `body.items.item.indctVal11`
 - `body.items.item.indctVal12`
 - `body.items.item.indctVal13`
 - `body.items.item.indctVal14`
 - `body.items.item.indctVal15`
 - `body.items.item.indctVal16`
 - `body.items.item.indctVal17`
 - `body.items.item.indctVal18`
 - `body.items.item.indctVal19`
 - `body.items.item.indctVal20`
 - `body.items.item.indctId`
 - `body.items.item.schlId`
 - `body.items.item.indctYr`

## 후속 작업에 바로 필요한 관찰

- API별로 코드 조회성 엔드포인트와 대학/학과/지표 조회성 엔드포인트가 혼재한다.
- DB 스키마 초안은 `body.items.item.*` 필드군을 기준으로 API별 테이블/코드 테이블 분리를 검토해야 한다.
- Swagger 기준 응답은 XML이지만, 실제 호출 시 XML/JSON 지원 여부와 nullable/반복 cardinality는 실응답 확인이 필요하다.
- 일부 엔드포인트는 동일한 공통 파라미터 집합을 공유하므로 수집기 구현 시 공통 요청 빌더로 묶기 쉽다.

## 미확정/운영 확인 필요

- 인증키 발급/쿼터/에러 응답 상세 형식
- `body.items.item`가 단건 객체인지 배열로 오는지에 대한 실제 직렬화 형태
- 연도/학교/학과 코드의 최신 유효 범위
- Swagger에 드러나지 않는 값 domain(코드값 실제 목록)과 데이터 누락 정책
