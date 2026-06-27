# Career 수집/DB 구축 구현 범위 및 검증 계획

## 기준 산출물

- 스키마 초안: `career/DB_SCHEMA.md`
- OpenAPI 샘플: `career/OpenAPIExample/jobdiclist.html`, `career/OpenAPIExample/jobdicview.html`
- 공급자 매뉴얼: `career/openAPI이용매뉴얼_v4.1.pdf`

## 현재 상태 점검

- 실제 개발·실행·테스트 기준은 서버 `/var/www/html/update/career` 다.
- 로컬 저장소는 서버 기준 코드/문서를 가져오는 **스냅샷 저장소**로 유지한다.
- 현재 스냅샷에는 다음이 반영돼 있다.
  - 통합 엔트리포인트: `career/update_career.py`
  - 복원/탐색용 개별 스크립트: `career/update_code.py`, `career/update_jobs.py`, `career/update_school.py`, `career/update_major.py`, `career/update_major_view.py`, `career/update_school_probe.py`
  - 공통 모듈: `career/include/crawler_common.py`
- 서버에는 최소 다음 cron 이 등록돼 있다.
  - 매월 코드표 동기화
  - 매주 직업 목록 동기화
  - 매월 직업 상세 동기화
- 따라서 이 문서는 **서버 운영 기준을 설명하는 로컬 스냅샷 문서**로 본다.

## SQL 초안 리뷰

### 유지해도 되는 점
- `code_list`, `job_list`, `school_list`, `subject_list`를 1차 구축 기준으로 둔 우선순위는 타당하다.
- 반복 노드를 1:N 테이블로 분리한 방향은 상세 API 적재 구조에 맞다.
- `recv_time` 공통 유지, 기존 운영 명칭(`subject`, `code_list`) 유지 원칙도 일관적이다.

### 보완이 필요한 점
- `career/OpenAPIExample/*.html`은 일부 필드명 예시만 보여주므로, 실제 적재 컬럼 확정은 PDF 명세나 실응답 샘플 재검증이 필요하다.
- `job_list`의 목록/상세 혼합 컬럼은 구현 시 응답 출처를 명확히 나눠야 한다.
  - 목록 API에서 채워지는 필드
  - 상세 API에서만 채워지는 필드
- 차트성 테이블(`edu_chart`, `major_chart`, `indicator_chart`)은 현재 PK가 `jcode` 단독이라 다건 응답이면 충돌 가능성이 있다.
  - 구현 전 실응답 기준으로 `seq` 또는 `label` 포함 여부 확인 필요
- `subject_detail_list` 계열은 학교급(`high`, `univ`)별 필드 편차가 있으므로 빈 문자열 저장 정책을 수집기 공통 규칙으로 못박아야 한다.

## 수집기 구현 범위

### 1차 구현 범위
1. 공통 코드 수집
   - 코드성 API 응답 적재
   - 대상: `code_list`
2. 직업 목록 수집
   - 직업 목록 API 페이지 순회
   - 대상: `job_list`
3. 학교 목록 수집
   - 학교 구분별 목록 수집
   - 대상: `school_list`
4. 학과 목록 수집
   - 학교급별 학과 목록 수집
   - 대상: `subject_list`

### 2차 구현 범위
1. 직업 상세 수집
   - 대상: `job_work_list`, `job_ready_list`, `forecast_list`, `perform_list`
2. 학과 상세 수집
   - 대상: `subject_detail_list`, `subject_chart_list`

### 3차 구현 범위
- 나머지 반복/부가 테이블 일괄 확장
- 차트/상담사례/관련기관/텍스트 묶음 적재

## 구현 제외 범위

- 웹 UI
- 운영/모니터링 화면
- PHP 라이브러리 계층
- 실제 운영 배포 자동화

## 구현 전 확인 필요 항목

1. 실제 수집기 소스 위치
   - 서버 `/var/www/html/update/career` 기준으로 확정
2. API 인증키 운영 방식 확정
   - 샘플 HTML에는 키가 하드코딩돼 있어 재사용 금지
3. 목록/상세 API별 응답 샘플 보관
   - 필드 nullable/배열 cardinality 확인 필요
4. 적재 단위 결정
   - 전체 재수집
   - 변경분 갱신
   - 실패 재시도 단위

## 검증 계획

### 문서 검증
- `DB_SCHEMA.md`의 모든 1차 대상 테이블이 구현 범위 문서와 일치하는지 대조
- 샘플 HTML의 필드명과 스키마 컬럼 설명 매핑 확인

### 수집기 구현 후 검증
1. API 연결 검증
   - 각 엔드포인트 1건 호출 성공
   - 필수 키 존재 확인
2. 파싱 검증
   - 목록/상세 응답에서 누락 필드, 빈 배열, null 처리 확인
3. DB 적재 검증
   - 1차 대상 테이블 upsert 성공
   - PK/중복 처리 확인
4. 샘플 데이터 검증
   - 직업 1건, 학교 1건, 학과 1건을 골라 원문과 DB 적재 결과 비교
5. 회귀 검증
   - 같은 데이터를 재수집해도 PK 충돌 없이 동일 결과 유지

### 지금 단계에서 가능한 검증
- 문서 간 정합성 검토
- 샘플 HTML과 스키마 초안 간 필드 대응 검토
- 서버 수집기/cron 상태와 문서 반영 여부 확인

## 리스크

- 로컬 저장소는 실행 기준점이 아니므로, 실행 기반 검증 증거는 서버에서만 확정된다.
- 샘플 HTML은 예제 수준이라 전체 응답 구조 보장 자료로 쓰기 부족
- API 키 하드코딩 예제가 남아 있어 문서/샘플 재사용 시 보안 사고 위험이 있다

## 결정

- 실제 개발/테스트/cron 검증은 서버에서 진행한다.
- 로컬은 서버 기준 코드와 문서를 따라가는 스냅샷으로 유지한다.
- 구현 착수/수정 여부 판단도 서버 실행 증거를 우선한다.
