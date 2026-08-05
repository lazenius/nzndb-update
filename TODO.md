<!-- 다음 세션 시작 메모 — 자동 생성, 수동 편집 금지 -->
> **마지막 세션:** 2026-08-05 | 로컬 `7df4baa` 이후 / 서버 `6316bbd`
>
> **완료한 작업:**
> - 첫 실실행(08-05 02:30) 점검 — 전량 적재 0건, 04:10 timeout kill, replay 락 충돌로 미실행 확인
> - 429 진짜 원인 규명: **엔드포인트당 일일 1,000회 한도**. 3일 연속 성공 호출이 정확히 1,000에서 끊김. 차단·제재 아님, 자정 리셋 정상
> - 원인은 indctId 팬아웃 — 유효 코드 2개(`66`,`67`)인데 83개 전량 곱함. `13학교 × 83 = 1,079 > 1,000` 로 설계 시점부터 한도 초과값
> - livelock 발견·해소 — 0건 응답 학교는 `recv_time` 이 안 올라가 같은 13개교 무한 재선정. `school_indicator_attempt` 대장 신설
> - 학교당 40콜(엔드포인트별 최대 754/1,000)로 축소 → **stale 롤링 폐기, 377개교 전량 매일 수집**으로 전환
> - 엔드포인트별 예산(900) + 429 서킷 브레이커(연속 5) 추가, 요청 지연 0.6/3.0초 → 0.1초
> - 크론 교체 완료 (잡 16→15): `--stale-limit 13` 제거, 04:10 replay 잡 삭제
> - 검증: 스모크 38콜/43행, 20개교 760콜 전량 성공, 브레이커 5건 정확 발동
> - **377개교 전량 수동 실행 실증** — 59분 53초, 14,326콜(=377×38) 성공, 적재 14,169행, 시도 대장 377개교 전원, 최대 소비 엔드포인트 754/1,000(75%)로 예산 900 적정 확인
>
> - **저장소 구조 정립 (08-06)** — 서버를 origin/main 에 재정렬해 06-27부터의 히스토리 분기 해소. 서버가 코드 SoT 겸 push 주체(`0a6b226`), 로컬은 sparse-checkout 으로 코드 없이 문서만. 규칙은 AGENTS.md §저장소 운용에 명문화
> - 단위 테스트 24개로 확장 (화이트리스트·예산 절단·브레이커·시도 대장 신규 4건), 전량 통과
>
> **남은 작업:**
> - 08-06 02:30 크론 경로 확인 — flock 획득·로그 append 정상 동작만 (수치는 전량 실행으로 선검증 완료)
> - 서버 `/var/www/html/update` 가 웹 루트 아래 — Nginx 에서 접근 차단돼 있는지 확인 (코드·문서 노출 여부)
> - 서버 `nzndb-update` push 미승인 — 서버 커밋 `a432584`, `6316bbd` 가 서버에만 있음
> - 서버 career, academyinfo 수집/DB 구축 계속 개발, 실유입 검증
> - robocode-admin/db/ 에 update DB 모니터링용 html/php 페이지 계속 구축
>
> **다음에 시작할 곳:** 08-06 02:30 배치 로그(`logs/sync_school_indicator_batch.log`) 확인 — `batch completed`·콜수 14,326+754 여부. RDS `max_connections` 확대·`MAX_USER_CONNECTIONS` 계정 격리는 설계문서 §11 후속 권고(별도 승인 필요).
<!-- /다음 세션 시작 메모 -->

- [ ] caveman 모드 적용 유지
- [x] 2026-08-05 academyinfo skip TSV 실발생분 재처리 후 누락 여부 재검증 → 11,338행 중 99.96%가 한도 소진분이라 재처리 무의미, replay 경로 폐기
- [x] 2026-07-02 로컬 도커 서버에 update 폴더 연결
- [x] 2026-08-05 academyinfo HTTP 429 원인 파악 — 엔드포인트당 일일 1,000회 한도 소진 (indctId 83개 팬아웃)
- [x] 2026-06-30 ECC 플러그인 설치 및 Codex 인식 확인

- [ ] 서버 career, academyinfo 수집/DB 구축 계속 개발, cron 등록, 실유입 검증
- [x] 2026-08-06 서버 nzndb-update push 정상화 — 서버를 origin/main 에 재정렬, 서버가 직접 push (`0a6b226`). 로컬은 sparse-checkout 문서 전용으로 전환
- [x] 2026-08-05 academyinfo school_indicator 첫 실실행 로그로 `--stale-limit 13` 재튜닝 → stale 롤링 폐기, 전량 매일 수집으로 전환
- [x] 2026-08-05 academyinfo school_indicator 전량 수집 실증 — 377개교 59분 53초, 14,326콜 성공, 적재 14,169행
- [ ] academyinfo school_indicator 크론 경로 확인 (08-06 02:30 flock 획득·로그 append)
- [ ] academyinfo skip TSV 아카이브(`logs/archive/sync_school_indicator_skips-20260805.tsv`) 폐기 여부 판단
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
- [x] 2026-08-05 academyinfo 수집을 엔드포인트 일일 한도(1,000회) 기반 전량 매일 수집으로 전환 — 429 원인이 indctId 83개 팬아웃에 의한 한도 소진임을 실측 규명, indctId 화이트리스트·엔드포인트 예산·429 서킷 브레이커·시도 대장(livelock 해소) 도입, 크론 잡 16→15 (서버 `6316bbd`)
- [x] 2026-08-05 [버그] academyinfo school_indicator_list OpenAPI HTTP 429 완화 및 롤링 cron 배치 안정화 — RDS 커넥션 고갈 장애 원인 규명, stale-first 롤링 전환, flock 도입, 크론 14슬롯 재배치, logrotate 설치
- [x] 2026-07-20 academyinfo 창업지원 적재 배치화 및 startup_support_list 학교·연도 인덱스 반영
- [x] 2026-07-06 academyinfo skip TSV 재처리 커맨드 설계/구현 및 서버 스모크 검증
- [x] 2026-07-06 career sync-job-detail 수동 실행 로그 파일 append 정리 및 서버 검증
- [x] 2026-07-06 [버그] career sync-job-detail 월배치 중 `Duplicate entry '173-318'` 무결성 오류로 중단
- [x] 2026-07-06 서버 career, academyinfo cron 정상 가동 여부와 최근 오류 로그 점검
- [x] 2026-07-06 서버 career, academyinfo cron 등록/최근 로그 점검 및 보완 작업 설계
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
