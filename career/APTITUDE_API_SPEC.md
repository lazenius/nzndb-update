# Career 적성검사 OpenAPI 스펙 초안

## 기준

- v1 안내 페이지: <https://www.career.go.kr/cnet/front/openapi/openApiTestCenter.do>
- v2 안내 페이지: <https://www.career.go.kr/cnet/front/openapi/openApiv2TestCenter.do>
- 이 문서는 **DB 설계 전 단계의 스펙 정리 문서**다.
- 현재 저장소 기준 `career` 메인 수집기(`update_career.py`)에는 아직 편입하지 않는다.

## 결론 요약

- `career`에는 **적성검사/진로심리검사 전용 OpenAPI 서비스가 별도로 있다.**
- 기존에 정리한 `aptds.json`은 **적성유형 코드 마스터**일 뿐이고, 이 문서의 대상은 **검사 문항/응답/결과표 URL**을 제공하는 API다.
- 서비스는 2계열이다.
  1. **v1**: 직업흥미검사(H) 제외 나머지 진로심리검사
  2. **v2**: 직업흥미검사(H) 전용

---

## 1. 서비스 구분

| 버전 | 용도 | 스펙 수 | 비고 |
|---|---|---:|---|
| v1 | 직업흥미검사(H) 제외 진로심리검사 | 2 | 문항 조회 + 결과 요청 |
| v2 | 직업흥미검사(H) | 3 | 목록 조회 + 문항 조회 + 결과 요청 |

---

## 2. v1 — 진로심리검사

### 개요

- 안내 문구 기준: **직업흥미검사(H)를 제외한** 커리어넷 진로심리검사를 제공
- 제공 엔드포인트:
  - 문항 요청
  - 결과 요청

### 2-1. 심리검사 문항 요청

- Method: `GET`
- URL:
  - `https://www.career.go.kr/inspct/openapi/test/questions?apikey=인증키&q=심리검사번호`

#### 요청 파라미터

| 이름 | 필수 | 설명 |
|---|---|---|
| `apikey` | 예 | 발급받은 OpenAPI 키 |
| `q` | 예 | 심리검사번호 |

#### 응답 핵심 필드

| 필드 | 설명 |
|---|---|
| `SUCC_YN` | 성공 여부 |
| `ERROR_REASON` | 오류 사유 |
| `RESULT[].question` | 문항 |
| `RESULT[].answer01~answer10` | 보기 |
| `RESULT[].answerScore01~answerScore10` | 보기 점수 |
| `RESULT[].tip1Score~tip3Score` | 보기 설명 위치 |
| `RESULT[].tip1Desc~tip3Desc` | 보기 설명 |
| `RESULT[].qitemNo` | 문항번호 |

### 2-2. 심리검사 결과 요청

- Method: `POST`
- URL:
  - `https://www.career.go.kr/inspct/openapi/test/report`
- Content-Type:
  - `application/json`

#### 요청 파라미터

| 이름 | 필수 | 설명 |
|---|---|---|
| `apikey` | 예 | 발급받은 OpenAPI 키 |
| `qestrnSeq` | 예 | 심리검사번호 |
| `trgetSe` | 예 | 검사자 타입 |
| `gender` | 예 | 성별코드 |
| `school` | 아니오 | 학교명 |
| `grade` | 예 | 학년 |
| `startDtm` | 예 | 검사 시작 timestamp |
| `answers` | 예 | 답변 문자열 |

#### 응답 핵심 필드

| 필드 | 설명 |
|---|---|
| `SUCC_YN` | 성공 여부 |
| `ERROR_REASON` | 오류 사유 |
| `RESULT.inspctSeq` | 검사결과 일련번호 |
| `RESULT.url` | 결과표 URL |

### 2-3. v1 페이지에 명시된 검사 종류

페이지 기준 확인된 대표 항목:

- 직업흥미검사(K) – 중학생
- 직업흥미검사(K) – 고등학생
- 진로개발준비도검사
- 이공계전공적합도검사
- 주요능력효능감검사
- 진로흥미탐색 – 초등학생
- 진로개발역량 – 초등학생
- 직업적성검사 – 중학생
- 직업적성검사 – 고등학생
- 진로성숙도검사 – 중학생
- 진로성숙도검사 – 고등학생
- 직업가치관검사 – 중학생
- 직업가치관검사 – 고등학생

> 즉, 사용자가 말한 “적성검사”는 최소한 v1의 `직업적성검사(중학생/고등학생)` 형태로 실제 OpenAPI 제공이 확인된다.

---

## 3. v2 — 직업흥미검사(H)

### 개요

- 안내 문구 기준: 커리어넷 진로심리검사 중 **직업흥미검사(H)** 제공
- 제공 엔드포인트:
  - 목록 요청
  - 문항 요청
  - 결과 요청

### 3-1. 심리검사 목록 요청

- Method: `GET`
- URL:
  - `https://www.career.go.kr/inspct/openapi/v2/tests?apikey=인증키`

#### 응답 핵심 필드

| 필드 | 설명 |
|---|---|
| `result[].qno` | 검사번호 |
| `result[].name` | 검사명 |
| `result[].description` | 설명 |
| `result[].summary` | 요약 |
| `result[].maker` | 제작자 |
| `result[].exectime` | 예상시간 |
| `result[].qcount` | 문항수 |
| `success` | 성공 여부 |
| `message` | 오류 메시지 |

#### 현재 페이지 기준 노출 검사

| qno | 이름 | 비고 |
|---:|---|---|
| `33` | 직업흥미검사(H) | 중학생 |
| `34` | 직업흥미검사(H) | 고등학생 |

### 3-2. 심리검사 문항 요청

- Method: `GET`
- URL:
  - `https://www.career.go.kr/inspct/openapi/v2/test?apikey=인증키&q=심리검사번호`

#### 요청 파라미터

| 이름 | 필수 | 설명 |
|---|---|---|
| `apikey` | 예 | 발급받은 OpenAPI 키 |
| `q` | 예 | 심리검사번호 (`33`, `34`) |

#### 응답 핵심 필드

| 필드 | 설명 |
|---|---|
| `result.summary` | 검사 설명 |
| `result.qnm` | 검사명 |
| `result.qno` | 검사번호 |
| `result.etime` | 예상시간 |
| `result.questions[]` | 문항 목록 |
| `result.questions[].no` | 문항번호 |
| `result.questions[].limit` | 허용 답변 수 |
| `result.questions[].text` | 문항 내용 |
| `result.questions[].title` | 상위 안내 문구 |
| `result.questions[].choices[]` | 선택지 |
| `result.questions[].choices[].val` | 선택값 |
| `result.questions[].choices[].text` | 선택지 텍스트 |
| `result.questions[].choices[].type` | `M` 선택형 / `I` 직접입력 |
| `result.maker` | 제작자 |
| `success` | 성공 여부 |
| `message` | 오류 메시지 |

### 3-3. 심리검사 결과 요청

- Method: `POST`
- URL:
  - `https://www.career.go.kr/inspct/openapi/v2/report`
- Content-Type:
  - `application/json`

#### 요청 파라미터

| 이름 | 필수 | 설명 |
|---|---|---|
| `apikey` | 예 | 발급받은 OpenAPI 키 |
| `answers` | 예 | 문항별 답변 배열 |
| `gender` | 예 | 성별코드 |
| `grade` | 예 | 학년 |
| `qno` | 예 | 검사번호 (`33` 또는 `34`) |
| `school` | 아니오 | 학교명 |
| `startdtm` | 예 | 검사 시작 timestamp |
| `trgetse` | 예 | 검사구분 |

#### 응답 핵심 필드

| 필드 | 설명 |
|---|---|
| `result.inspct.enddtm` | 완료일시 |
| `result.inspct.school` | 학교명 |
| `result.inspct.grade` | 학년 |
| `result.inspct.qestnrseq` | 검사구분번호 |
| `result.inspct.inspctseq` | 검사결과번호 |
| `result.inspct.reporturl` | 결과표 URL |
| `result.inspct.trgetse` | 검사구분 |
| `result.inspct.sexdstn` | 성별 |
| `success` | 성공 여부 |
| `message` | 오류 메시지 |

---

## 4. DB 구축 관점 정리

## 지금 당장 DB를 만들 필요가 없는 이유

- 이 API는 **마스터 데이터 적재형**보다 **실시간 검사 수행형**에 가깝다.
- 핵심 산출물이:
  - 문항 세트
  - 사용자 답변
  - 결과표 URL
  이므로, `academyinfo`/기존 `career` 마스터 수집처럼 단순 정기 적재 대상과 성격이 다르다.

## 그래도 저장을 검토할 수 있는 데이터

### 선택지 A — DB 없이 문서/API 클라이언트만

- 사용 목적:
  - 사이트/서비스에서 실시간 검사 연결
  - 별도 저장 없이 결과 URL만 사용자에게 제공

### 선택지 B — 최소 로그성 저장

- 후보 테이블:
  - 검사 메타 (`test_type`, `version`, `qno`, `name`)
  - 실행 로그 (`inspctseq`, `reporturl`, `trgetse`, `gender`, `grade`, `startdtm`, `enddtm`)
- 단, **개인 응답(answer)** 저장은 개인정보/민감정보 검토가 먼저다.

### 선택지 C — 문항 캐시 저장

- 문항 API 응답이 자주 바뀌지 않는다면
  - `question_set`
  - `question_item`
  정도 캐시 테이블로 관리 가능
- 하지만 현재 단계에서는 **문서화 우선**이 맞다.

---

## 5. 현재 저장소 기준 상태

| 대상 | 상태 |
|---|---|
| 적성검사 API 존재 확인 | 예 |
| v1/v2 스펙 문서화 | 예 |
| DB 스키마 설계 | 아니오 |
| 수집/연동 프로그램 개발 | 아니오 |

## 권장 다음 단계

1. 이 API를 **DB 적재형**으로 볼지, **실시간 연동형**으로 볼지 먼저 결정
2. 실시간 연동형이면:
   - `career` 수집기와 분리된 **검사 API 클라이언트 문서**로 관리
3. DB 적재형이면:
   - 개인정보/민감정보 저장 범위부터 결정
   - 결과 URL 로그만 저장할지, 문항/답변까지 저장할지 구분
