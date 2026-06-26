# CHANGELOG

## 2026-06-26

### academyinfo
- `README.md`를 URL 목록 중심 문서에서 운영 개요 문서로 재작성
- `COLLECTION_PLAN.md` 추가
  - 103개 스펙의 수집 주기 분류
  - cron 편성 기준
  - 학교 마스터 `latest` 실행 시 유효연도 fallback 정책 반영
- `include/README.md` 추가
- `update_academyinfo.py` 추가
  - 코드/년도
  - 학교 마스터
  - 학과 마스터
  - 학교별 지표
  - 지역별 지표
  - 산학협력
  수집 작업 엔트리포인트 초안
- `include/common.py` 추가
  - DB 연결
  - XML 응답 파싱
  - raw 응답 저장
  - API URL 조합 공통 처리
- `include/common_local.py.example` 추가

### 프로젝트 공통
- `AGENTS.md`를 현재 상태에 맞게 갱신
  - 서버 Git 저장소 / GitHub 원격 연결 상태 반영
  - 로컬은 GitHub 원격을 연결하지 않는 원칙 명시
- `.gitignore` 추가
  - `.omx/`
  - `.DS_Store`
  - Python 캐시 제외
- WIP 정리 문서 최신화
  - `career` 학교/학과 수집 통합 상태를 현재 코드 기준으로 정정
  - `academyinfo` `HTTP 429` 운영 안정화안 문서화
  - `robocode-admin` 1차 모니터링 후속 정의 구체화

### 서버 반영 상태
- 서버 `/var/www/html/update` Git 저장소 초기화
- GitHub `lazenius/nzndb-update` 생성 및 origin 연결
- 서버 `main` 초기 커밋/푸시 완료
- academyinfo cron 등록 완료
