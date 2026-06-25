# Academyinfo

## 목적

- 한국대학교육협의회 `academyinfo` OpenAPI 9개 서비스를 분석하고
- 수집/적재 스키마, 구현 범위, 수집 주기, cron 운영 기준을 정리하는 문서/수집기 기준 디렉터리

## 현재 상태

- 스펙 분석 완료: **103개 엔드포인트**
- 스키마 초안 완료: **7개 테이블**
- 수집기 초안 작성 완료: `academyinfo/update_academyinfo.py`
- 서버 cron 등록 완료: `/var/www/html/update/academyinfo`
- 메타데이터 초기 적재 검증 완료
  - `code_list`
  - `year_list`
- 학교 마스터는 `latest` 실행 시 **빈 최신연도(예: 2026)** 를 건너뛰고 최근 유효연도로 fallback 하도록 반영됨

## 주요 파일

- `API_SPEC.md`
  - 9개 서비스 / 103개 엔드포인트 기준 명세
- `DB_SCHEMA.md`
  - `ACADEMYINFO_DB` 7개 테이블 초안
- `IMPLEMENTATION_SCOPE.md`
  - 구현 우선순위, 단계별 작업 순서, 검증 체크리스트
- `MAPPING_GAP_REPORT.md`
  - 스펙 ↔ 스키마 매핑 누락 점검
- `COLLECTION_PLAN.md`
  - 수집 주기, cron 편성, 운영 제약
- `update_academyinfo.py`
  - 수집기 엔트리포인트
- `include/common.py`
  - DB 연결, API 호출, XML 파싱 공통 모듈
- `include/common_local.py.example`
  - 서버 전용 설정 예시

## 서비스 원천

1. 한국대학교육협의회_대학알리미 대학 기본 정보_GW  
   https://www.data.go.kr/data/15158963/openapi.do
2. 한국대학교육협의회_대학알리미 교육여건 현황_GW  
   https://www.data.go.kr/data/15158679/openapi.do
3. 한국대학교육협의회_대학알리미 교원·연구 현황_GW  
   https://www.data.go.kr/data/15158678/openapi.do
4. 한국대학교육협의회 대학정보공시 학생 현황_GW  
   https://www.data.go.kr/data/15158684/openapi.do
5. 한국대학교육협의회_대학알리미 재정 현황_GW  
   https://www.data.go.kr/data/15158680/openapi.do
6. 한국대학교육협의회_대학 학과 정보_GW  
   https://www.data.go.kr/data/15158955/openapi.do
7. 한국대학교육협의회_대학별 학과정보_GW  
   https://www.data.go.kr/data/15158666/openapi.do
8. 한국대학교육협의회_대학 및 전문대학정보_GW  
   https://www.data.go.kr/data/15158665/openapi.do
9. 한국대학교육협의회_대학알리미 산학협력 현황_GW  
   https://www.data.go.kr/data/15158626/openapi.do

## 서버 운영 기준

- 서버 경로: `/var/www/html/update/academyinfo`
- cron 등록: 서버 `crontab`
- 로그 경로: `academyinfo/logs/`
- raw 응답 경로: `academyinfo/raw/`
- 비밀값 파일:
  - 실제값: `include/common_local.py` (서버 전용, git 제외)
  - 예시값: `include/common_local.py.example`

## 실행 예시

```bash
cd /var/www/html/update/academyinfo
python3 update_academyinfo.py plan
python3 update_academyinfo.py sync-code-year --scope latest
python3 update_academyinfo.py sync-school-master --scope latest
```

## 주의

- `career`처럼 이 디렉터리도 아직 완성된 제품 저장소는 아니다.
- 실제 운영에서는 실응답 기준으로 PK/nullable/연도 fallback 정책을 계속 다듬어야 한다.
- `AGENTS.md` 상위 설명 중 일부는 현재 상태(서버 git 저장소, GitHub 연결 완료)와 차이가 있으나 아직 미갱신 상태다.
