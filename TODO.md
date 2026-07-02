<!-- 다음 세션 시작 메모 — 자동 생성, 수동 편집 금지 -->
> **마지막 세션:** 2026-06-27 | 커밋 `(현재 HEAD)`
>
> **완료한 작업:**
> - career 적성검사 v2 메타 캐시 수집기 및 서버 cron 추가
> - academyinfo school_indicator 실측 기반 롤링 cron 재설계
> - 서버 수동 스모크/실측 및 로그 마스킹 검증
>
> **남은 작업:**
> - 서버 career, academyinfo 수집/DB 구축 계속 개발, cron 등록, 실유입 검증
> - [버그] academyinfo school_indicator_list 수집 시 OpenAPI HTTP 429 완화 및 롤링 cron 배치 안정화
> - robocode-admin/db/ 에 update DB 모니터링용 html/php 페이지 계속 구축
>
> **다음에 시작할 곳:** academyinfo school_indicator 롤링 cron 첫 실실행 결과와 robocode-admin batch 로그 기준 반영
<!-- /다음 세션 시작 메모 -->

- [ ] caveman 모드 적용 유지
- [x] 2026-07-02 로컬 도커 서버에 update 폴더 연결
- [ ] 서버 career, academyinfo cron 정상 가동 여부와 최근 오류 로그 점검
- [ ] academyinfo HTTP 429, school_master lock wait timeout 원인 파악
- [x] 2026-06-30 ECC 플러그인 설치 및 Codex 인식 확인

- [ ] 서버 career, academyinfo 수집/DB 구축 계속 개발, cron 등록, 실유입 검증
- [ ] [버그] academyinfo school_indicator_list 수집 시 OpenAPI HTTP 429 완화 및 롤링 cron 배치 안정화
- [ ] (나중에) academyinfo school_indicator 롤링 cron 첫 실실행 후 batch 로그/누락 건수 검증
- [ ] (나중에) robocode-admin school_indicator 모니터링 로그 기준을 a~d 에서 batch 로 변경
- [ ] (나중에) career sync-subject-detail 월배치 첫 실실행 후 로그/적재 건수 검증
- [ ] (나중에) career sync-aptitude-meta 월배치 첫 실실행 후 로그/적재 건수 검증
- [ ] (나중에) career aptitude v1 검사번호 목록 확인 후 문항 캐시 확장

- [x] 2026-06-26 career 적성검사 API 사용자용 웹 연동 설계 문서 작성

- [x] 2026-06-27 academyinfo/career 스펙 구현 범위 1~3번 분석 (부분구현 목록, 미구현 표, 코드 기준 endpoint 체크리스트)

- [ ] robocode-admin/db/ 에 update DB 모니터링용 html/php 페이지 계속 구축
- [ ] omx team으로 nznlab 조회 라이브러리 구현 및 robocode-admin 연동 테스트
- [x] 2026-06-27 robocode-admin/db 모니터링 1차 구현 (스펙 전체보기, 학교 조회, 학과 조회, 수집 로그)
- [ ] (나중에) 서버 academyinfo/common.py 미추적 파일 정리
- [ ] 지난 세션 중단된 omx team 상태 점검 및 재개

- [x] 2026-06-26 update / robocode-admin 역할 분리 문서화





- [ ] robocode-admin/db/index.html 에 career, academyinfo 모니터링 링크 목록 추가
- [ ] 서버 robocode-admin/db/index.html 반영
- [ ] 로컬 도커 서버 robocode-admin/db/index.html 반영
- [ ] 서버 robocode-admin 세션 저장 경로 권한 수정
- [ ] 서버 admin.roboco.de Nginx index 우선순위 html 우선으로 수정
- [ ] robocode-admin/db 서버본을 로컬에도 동기화
- [ ] nznlab/db/career, academyinfo 서버본을 로컬에도 동기화
## 완료
- [x] 2026-06-28 robocode-admin/db 전체 모니터링 및 학교/학과 조회 점검
- [x] 2026-06-28 nznlab/db academyinfo, career 스펙 재점검 및 누락 재확인
- [x] 2026-06-28 nznlab/db academyinfo, career 스펙 누락 점검 및 보강
- [x] 2026-06-28 robocode-admin/db 외부 진입용 html 래퍼 추가 및 링크 전환
- [x] 2026-06-28 collector_runs 운영 기준 로그 목록 단일 소스화
- [x] 2026-06-28 robocode-admin/db 백업 .bak-* 및 html/php 역할 기준 문서화
- [x] 2026-06-28 nznlab 대시보드 요약 라이브러리 추가 후 robocode-admin/db/index 분리
- [x] 2026-06-28 robocode-admin/db/common.php 남은 helper 사용처 정리
- [x] 2026-06-28 nznlab spec 문서 조회 라이브러리 추가 후 robocode-admin/db/specs.php 분리
- [x] 2026-06-28 nznlab/db/career, nznlab/db/academyinfo 조회 라이브러리 초안 작성 후 robocode-admin/db SQL 분리
- [x] 2026-06-28 nznlab/db academyinfo/career collector_runs 라이브러리 추가 및 robocode-admin 연동
- [x] 2026-06-27 nznlab/db/career subjects 조회 라이브러리 추가 및 robocode-admin 연동
- [x] 2026-06-27 nznlab/db/career status 조회 라이브러리 추가 및 robocode-admin 연동
- [x] 2026-06-27 robocode-admin/db/schools.php 분리 상태 재검증 완료
- [x] 2026-06-27 nznlab/db/academyinfo subjects/status 조회 라이브러리 추가 및 robocode-admin 연동
- [x] 2026-06-27 omx team으로 update 수집기/cron + nznlab/robocode-admin 모니터링 후속 진행
- [x] 2026-06-27 nznlab/db/career, nznlab/db/academyinfo 조회 함수로 schools.php SQL 실제 분리
- [x] 2026-06-27 academyinfo school_indicator 배치 실행 시간 측정 및 cron batch 크기 재조정 검토
- [x] 2026-06-27 career, academyinfo 수집 프로그램 추가 개발 및 cron 등록 후속
- [x] 2026-06-27 [버그] academyinfo sync-school-indicators 가 3개 학교 배치도 장시간 실행되는 원인 분석
- [x] 2026-06-27 career, academyinfo 데이터 수집 프로그램 계속 개발 및 cron 등록
- [x] 2026-06-27 omx team으로 academyinfo 429/cron/monitoring 후속 진행
- [x] 2026-06-26 omx team으로 update 프로젝트 병렬 정리 실행
- [x] 2026-06-26 career school_list / subject_list 수집 명령 추가 및 서버 실적재 검증
- [x] 2026-06-26 academyinfo school_indicator 수집에 중간 commit / 429 retry 반영
- [x] 2026-06-26 robocode-admin/db/ 1차 상태 페이지 html/php 초안 작성
- [x] 2026-06-26 update / robocode-admin 역할 분리 문서 작성
- [x] 2026-06-26 career 적성검사 웹 연동 계획 문서 작성
- [x] 2026-06-26 career 적성검사 OpenAPI(v1/v2) 확인 및 스펙 문서 초안 작성
- [x] 2026-06-26 미구현/부분구현 빠른 확인용 `IMPLEMENTATION_GAPS.md` 작성
- [x] 2026-06-26 career, academyinfo 서비스/스펙/DB/수집기 상태 매트릭스 문서 작성
- [x] 2026-06-26 [버그] career sync-code-list 로그 건수 0 표시 원인 확인
- [x] 2026-06-26 로컬 career 스냅샷을 서버 기준 코드/문서로 동기화
- [x] 2026-06-26 academyinfo sync-subject-master 장기 실행 원인 확인 및 필요시 중단
- [x] 2026-06-26 academyinfo sync-subject-master 원인 분석 및 배치 단위 실행 수정
- [x] 2026-06-26 서버 개발/테스트 기준으로 파일 구조 및 문서 정리
- [x] 2026-06-26 .omx ignore 처리 및 변경 요약 문서화
- [x] 2026-06-26 AGENTS.md 최신 상태 반영 및 로컬 커밋
- [x] 2026-06-26 academyinfo 문서 구조 정리 및 최신 운영 상태 반영
- [x] 2026-06-26 서버 /var/www/html/update 초기 커밋 및 origin main 푸시
- [x] 2026-06-26 lazenius/nzndb-update 생성 또는 확인 후 서버 origin 연결
- [x] 2026-06-26 서버 /var/www/html/update git 저장소 초기화
- [x] 2026-06-25 academyinfo 103개 스펙 주기 산정, 수집기 작성, cron 등록
- [x] 2026-06-25 [버그] career/OpenAPIExample 샘플의 OpenAPI 키 하드코딩 제거
- [x] 2026-06-25 academyinfo IMPLEMENTATION_SCOPE.md에 Medium/Low 매핑 누락 반영 정리
- [x] 2026-06-25 caveman 모드 적용 대상 확인 및 응답
- [x] 2026-06-25 academyinfo 매핑 리포트 기준 문서 후속 반영
- [x] 2026-06-25 academyinfo 문서 기준 omx team 후속 작업 진행
- [x] 2026-06-25 academyinfo 9개 OpenAPI 세부 명세 분석 및 문서 초안 작성
- [x] 2026-06-25 academyinfo Task3: 구현 범위·검증 계획 작성
- [x] 2026-06-25 academyinfo Task2: DB 스키마 초안 작성
- [x] 2026-06-25 academyinfo Task1: API 명세 초안 작성
- [x] 2026-06-25 omx team 으로 career 수집/DB 구축 작업 병렬 진행
- [x] 2026-06-25 career Task2: 구현 범위·검증 계획 문서화
- [x] 2026-06-25 로컬 md 갱신 후 서버 git 저장소에서 커밋/푸시
- [x] 2026-06-25 ssh nazuni.net 접속해 /var/www/html/update 프로젝트 상태 확인
- [x] 2026-06-25 career PDF 기준 DB 스키마 md 작성 및 기존 테이블 명명 규칙 반영
- [x] 2026-06-26 career 스펙 수/테이블 수 확정
- [x] 2026-06-26 career 수집 주기 산정
- [x] 2026-06-26 career COLLECTION_PLAN.md 작성
- [x] 2026-06-26 career 수집기 초안 작성
- [x] 2026-06-26 career 서버 설정 연결 및 1회 검증
