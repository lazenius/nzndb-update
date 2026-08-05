# AGENTS.md

## 프로젝트 성격

- 프로젝트명: `update`
- 로컬 경로: `_lab/www/html/update` (문서 전용, git 없음)
- 서버 경로: `/var/www/html/update` (코드 원본, git + GitHub)
- 역할: DB 수집/적재 파이프라인

## 현재 원칙

- 이 프로젝트는 **도메인별 수집/적재 자산을 모으는 기준 저장소**다. 현재 `academyinfo`, `career`.
- **개발·실행·테스트·cron 검증은 전부 서버 `/var/www/html/update` 에서 한다.**
- 런타임 산출물(`logs/`, `raw/`)과 비밀 설정(`common_local.py`)은 Git 추적 대상에서 제외한다.

## 파일이 어디 있나

| 종류 | 위치 | 비고 |
|---|---|---|
| 수집기 코드 (`update_academyinfo.py`, `update_career.py`) | 서버만 | 로컬 사본 없음 |
| 단위 테스트 (`academyinfo/tests/`) | 서버만 | `python3 -m unittest discover -s tests` |
| crontab 스냅샷 (`deploy/crontab.ec2-user`) | 서버만 | 크론 변경 시 `crontab -l >` 로 갱신 |
| 스펙·설계 문서 (`*.md`, `docs/`) | 로컬에서 편집 → 서버로 올려 커밋 | 양쪽에 존재 |
| 비밀 설정 (`include/common_local.py`) | 서버만 | git 제외, `_lab/CLAUDE.local.md` 가 SoT |
| 로그·원본 XML (`logs/`, `raw/`) | 서버만 | git 제외, logrotate 적용 |

## 저장소 운용 (2026-08-06 정립 — irio 방식)

**git 은 서버에만 둔다. 로컬에는 git 도 소스코드도 없다.** `irio/aws_*` 와 동일 구조다.

| 위치 | 내용 | git |
|---|---|---|
| 서버 `/var/www/html/update` | 소스코드 · 테스트 · 실행 · 검증 | ✅ GitHub `lazenius/nzndb-update` |
| 로컬 `_lab/www/html/update` | 지침·기준 문서만 (`*.md`, `docs/`) | ❌ 없음 |

- **커밋·push 주체는 서버 하나뿐이다.** 코드를 고쳤으면 서버에서 바로
  `git add -A && git commit && git push`.
- 로컬에는 코드 사본을 두지 않는다. 코드를 봐야 하면 `ssh nazuni.net` 으로 읽는다.
- 로컬에서 `/ship` 은 쓰지 않는다 (git 이 없다). 서버 커밋은 명시적으로 지시한다.
- 문서는 로컬에서 편집하고, 의미 있는 변경이면 `scp` 로 서버에 올려 **서버에서 커밋**한다.
  로컬 문서 자체에는 이력이 없으므로 GitHub 사본이 유일한 백업이다.

### 작업 절차

```bash
# 코드 수정 (전부 서버에서)
ssh nazuni.net
cd /var/www/html/update/academyinfo
# ... 수정 ...
python3 -m unittest discover -s tests      # 커밋 전 필수
cd /var/www/html/update
git add -A && git commit -m "fix: ..." && git push

# 문서 수정 (로컬 편집 → 서버 반영)
scp AGENTS.md nazuni.net:/var/www/html/update/AGENTS.md
ssh nazuni.net "cd /var/www/html/update && git add -A && git commit -m 'docs: ...' && git push"
```

> 2026-06-27 ~ 08-05 사이 로컬에도 git 이 있어 양쪽에서 커밋이 이뤄졌고, 같은 작업이
> 다른 해시로 중복돼 히스토리가 분기했다. 08-06 에 서버를 origin/main 으로 재정렬하고
> 로컬 git 을 제거해 커밋 주체를 하나로 만들었다. 구조상 재발이 불가능하다.

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
