# CHANGELOG

## 2026-08-06

### 저장소 구조
- **git 을 서버 한 곳으로 통일** (irio/aws_* 와 동일 구조)
  - 서버 `/var/www/html/update` = 코드 원본 + git + GitHub, 유일한 커밋·push 주체
  - 로컬 `_lab/www/html/update` = 문서 전용, git 없음, 코드 사본 없음
  - 06-27부터 로컬·서버 양쪽에서 커밋이 이뤄져 같은 작업이 다른 해시로 중복되고
    히스토리가 분기해 있었다. 서버를 `origin/main` 에 재정렬해 해소한 뒤 로컬 git 제거
- `AGENTS.md` §저장소 운용·§파일이 어디 있나 추가

### academyinfo
- 수집을 **엔드포인트 일일 한도(1,000회) 기반 377개교 전량 매일 수집**으로 전환
  - indctId 화이트리스트 — `key_indicator` 83개 전량 곱을 유효 코드(`66`,`67`)로 축소
  - 엔드포인트별 일일 호출 예산 900회, 초과 시 시도가 오래된 학교부터 처리
  - `school_indicator_attempt` 대장 신설 — 0건 응답도 시도로 기록해 회전 정지 해소
  - 엔드포인트 단위 429 서킷 브레이커(연속 5건)
  - 요청 지연 0.6s/3.0s → 0.1s
- stale-first 롤링(`--stale-limit`)·skip replay 크론 폐기, 크론 잡 16 → 15
- 단위 테스트 20 → 24개
- 실측: 377개교 59분 53초, 14,326콜 성공, 적재 14,169행, 최대 소비 754/1,000

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
