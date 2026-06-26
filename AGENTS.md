# AGENTS.md

## 프로젝트 성격

- 프로젝트명: `update`
- 로컬 경로: `web/html/update`
- 서버 경로: `/var/www/html/update`
- 역할: DB 수집/적재 파이프라인 프로젝트의 로컬 기준점

## 현재 원칙

- 이 프로젝트는 여전히 **도메인별 수집/적재 자산을 모으는 기준 저장소**다.
- 현재는 `academyinfo`, `career` 기준 문서와 일부 수집기 스크립트가 함께 관리된다.
- Git 저장소는 초기화되었지만, **로컬 작업본은 GitHub 원격을 연결하지 않는다.**
- 서버 `/var/www/html/update` 는 Git 저장소 및 GitHub `lazenius/nzndb-update` 원격과 연결되어 있다.
- **실제 프로그램 개발·실행·테스트·cron 검증은 서버 `/var/www/html/update` 기준으로 진행한다.**
- 로컬 `/Users/nazuni/_lab/www/html/update` 는 문서·구조·기준 스냅샷 관리용으로 유지한다.
- 런타임 산출물(`logs/`, `raw/`)과 비밀 설정(`common_local.py`)은 Git 추적 대상에서 제외한다.

## 책임 범위

- 여러 도메인(`career`, `academyinfo`, 이후 추가 대상)의 수집기 자산이 최종적으로 모일 기준 프로젝트다.
- 웹 UI는 이 프로젝트 책임이 아니다.
- PHP 라이브러리 계층은 `nznlab` 책임이다.
- 관리/모니터링 화면은 `robocode-admin` 책임이다.

## 운영 분업 원칙

- 서버 `/var/www/html/update` 는 실제 **수집기 개발, DB 구축, cron 실행, 적재 검증** 기준점이다.
- `career` 적성검사 API처럼 **사용자 상호작용이 필요한 기능**은 DB 적재보다 **웹 연동 여부**를 먼저 판단한다.
- 관리/모니터링용 페이지는 서버 `robocode-admin/db/` 아래의 **단순 PHP/HTML 페이지**로 구축한다.
- `update` 프로젝트는 모니터링 UI를 직접 품지 않고, **데이터 구축/상태 제공 책임**에 집중한다.

## 향후 예정

- 필요 시 하위 도메인별 디렉터리 추가
  - 예: `career/`, `academyinfo/`
- 필요 시 수집 실행 기준 문서, 배포 기준 문서 추가
- 서버 기준 GitHub 저장소 `nzndb-update` 구조를 계속 이 프로젝트 설명에 맞춰 정리한다.
