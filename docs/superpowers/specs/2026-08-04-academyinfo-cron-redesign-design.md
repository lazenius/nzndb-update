# academyinfo 수집 크론 재설계

- 작성일: 2026-08-04
- 대상: 서버 `/var/www/html/update` (academyinfo, career 수집 크론)
- 계기: 2026-08-03 ~ 08-04 RDS 커넥션 고갈 및 사이트 접속 장애

> **2026-08-05 개정 — 이 문서의 §4 스케줄·§5.1 대상 선정·§5.3 429 처리는 폐기되었다.**
> 첫 실실행(08-05 02:30) 점검에서 429의 진짜 원인이 **OpenAPI 엔드포인트당 일일 1,000회
> 한도**임이 확정되어, stale 롤링 자체가 불필요해졌다. 확정된 현행 설계는 문서 맨 끝
> [§13 2026-08-05 개정](#13-2026-08-05-개정--엔드포인트-일일-한도-기반-전량-수집) 을 볼 것.

---

## 1. 배경 — 장애 원인 분석

### 1.1 증상

2026-08-03 새벽부터 08-04 13:26 까지 약 35시간 동안 RDS 커넥션이 잠식되어
여러 사이트에서 접속 장애가 발생했다.

### 1.2 확정된 사실

로그 `academyinfo/logs/sync_school_indicator_batch.log` 실측 기준이다.

**프로세스 누적** — 동시각에 로그를 쓰는 서로 다른 `offset=` 값의 개수:

| 시각 | 동시 실행 배치 수 |
|---|---|
| 08-03 12:00 | 19 |
| 08-03 21:00 | 24 |
| 08-04 03:00 | 27 |
| 08-04 09:00 | 27 |
| 08-04 13:26 | 26 → 전량 중단 |

크론은 08-03 02:10 ~ 22:40 에 30분 간격으로 42회 발사했고, 발사분이 거의 전부
생존해 누적되었다. 완주한 배치는 42개 중 2개뿐이다.

**런타임 폭주:**

```
[batch] offset=0 limit=9   → 08-03 02:10 발사, 03:01:28 완료 (51분, skips=0)
[batch] offset=9 limit=9   → 08-03 02:40 발사, 08-04 09:47:36 완료 (31시간 27분, skips=475)
```

**RDS 고갈의 직접 증거** — career `sync-subject-detail` (08-04 02:30 정상 발사)의 종료 로그:

```
pymysql.err.OperationalError: (1040, 'Too many connections')
```

수집기 프로세스 누적이 다른 수집 잡까지 죽였음이 로그로 확인된다.

### 1.3 인과 사슬

```
배치 1회 소요 51분 > 크론 간격 30분
        ↓ 구조적 중첩 (첫날부터 필연)
동시 API 호출 → OpenAPI HTTP 429
        ↓ 429 요청당 time.sleep(180)
런타임 증가 → 중첩 심화 (양성 피드백)
        ↓ 27 프로세스 × pymysql 커넥션 각 1개
RDS max_connections 고갈 → (1040) → 사이트 접속 장애
```

offset=9 배치의 skip 475건 × 180초 = 23.75시간. 총 소요 31시간 27분 중 대부분이
순수 sleep이다.

### 1.4 핵심 판단

`timeout` · `flock` 은 증상 억제다. 한 달치 전량(378학교 × 약 244요청 ≈ 92,000 요청,
순수 약 36시간 분량)을 20시간 창에 밀어넣은 **스케줄 설계 자체가 원인**이다.

또한 단독 실행이던 offset=0 배치(08-03 02:10)의 skip은 0건이었다.

> **2026-08-04 20:00 스모크로 정정.** 위 관찰만 보고 "429는 중첩의 결과지 원인이 아니다"라고
> 판단했으나 틀렸다. 중첩이 전혀 없는 `--stale-limit 1` 단독 실행에서도 429가 계속 발생했다
> (17분간 반영 14 / skip 18, 전부 `getComparisonFullTimeFacultyResearchCrntSt` 의 indctId 요청).
>
> 정확한 진술은 이렇다. **중첩은 RDS 고갈의 원인이 맞지만, 429는 중첩과 무관하게도 발생한다.**
> 02:10 야간 배치가 skip 0건이었던 것은 중첩이 없어서가 아니라 **시간대 차이**로 보인다.
> OpenAPI 쪽에 시간대별 부하 또는 쿼터 제한이 별도로 존재한다.
>
> 설계에 미치는 영향은 제한적이다. skip 기록 + replay 구조가 이 경우를 이미 커버하고,
> `--max-consecutive-skips` 와 `timeout` 이 런타임 상한을 준다. 다만 **야간 실행에서도 429
> 비율이 높다면 `--stale-limit 13` 이 74분을 넘길 수 있다.** 첫 실실행 로그로 재조정한다
> (§8 검증 항목).

---

## 2. 실측 기준값

### 2.1 작업량

| 항목 | 값 |
|---|---|
| endpoint 수 | 38 (`indctId` 로 곱해지는 것 2개) |
| 요청 수 / 학교 | 약 244 |
| 대상 학교 수 (scope=latest) | 378 |
| 소요 / 학교 (clean) | 340초 |

### 2.2 전 잡 실소요

| 잡 | 주기 | 실소요 |
|---|---|---|
| academyinfo school-indicators | 롤링 | 340초/학교 |
| academyinfo startup-support | 월(5일) | 115분 |
| academyinfo subject-master | 주(월) | 4분 |
| academyinfo regional-indicators | 월(4일) | 2분 |
| academyinfo school-master | 주(월) | 45초 |
| academyinfo code-year | 월(1일) | 26초 |
| career job-detail | 월(3일) | 1분 |
| career subject-detail | 월(4일) | 2분 |
| career code-list / job-list / school-list / subject-list / aptitude-meta | 주·월 | 각 10초 미만 |

무거운 잡은 **school-indicators** 와 **startup-support** 둘뿐이다. 나머지는 전부 5분 미만이라
시간 분산이 쉽다.

---

## 3. 설계 결정

| # | 결정 사항 | 선택 |
|---|---|---|
| D1 | 전량 갱신 주기 | 매일 롤링, 한 달에 한 바퀴 |
| D2 | 429 처리 | 즉시 skip 기록 + 별도 재처리 창 |
| D3 | 대상 선정 | `recv_time` 오래된 순 (자가 치유) |

### D1 근거

13학교/일 × 340초 = 약 74분. 378 ÷ 13 = 29.1일 → 한 달 한 바퀴.
현행 의도(월 1회 전량)와 커버리지가 동일하면서 일일 부하는 얕게 깔린다.

### D2 근거

`include/common.py` 의 `fetch_pages` 가 이미 429에 대해 4회 재시도 + 지연을 수행한다
(`재시도 예정: HTTP 429 ... attempt=4` 로그). 그 뒤 `update_academyinfo.py:1366` 이
추가로 180초를 자는 것은 이중 백오프다. 이를 제거하면 실행 시간이 요청 수에 비례해 고정된다.

재처리 경로는 `replay_school_indicator_skips` (`update_academyinfo.py:1378`) 와
`sync_school_indicator_skips.tsv` 로 이미 구현되어 있다. 크론 슬롯만 추가하면 된다.

### D3 근거

`school_indicator_list.recv_time` 이 upsert마다 `NOW()` 로 갱신된다
(`recv_time=VALUES(recv_time)`). 학교별 마지막 수집 시각이 이미 DB에 있으므로
별도 커서 저장소 없이 대상 선정이 가능하다.

기존 날짜 파생 offset 방식의 치명적 약점은 **실행이 실패하면 그 학교들이 다음 달까지
영구 유실**된다는 점이다. `recv_time` 오래된 순은 429로 빠진 학교, 중단된 실행분,
신규 추가 학교가 자동으로 다음 순번 앞으로 오므로 자가 치유된다.

---

## 4. 스케줄

| 시각 | 주기 | 잡 | 예상 소요 |
|---|---|---|---|
| 01:00 | 매월 1일 | academyinfo `sync-code-year` | 30초 |
| 01:05 | 매월 1일 | career `sync-code-list` | 5초 |
| 01:10 | 매주 월 | academyinfo `sync-school-master` | 1분 |
| 01:15 | 매주 월 | academyinfo `sync-subject-master` | 4분 |
| 01:25 | 매주 월 | career `sync-job-list` | 10초 |
| 01:30 | 매주 월 | career `sync-school-list` | 10초 |
| 01:35 | 매주 월 | career `sync-subject-list` | 10초 |
| 01:40 | 매월 3일 | career `sync-job-detail` | 1분 |
| 01:45 | 매월 4일 | career `sync-subject-detail` | 2분 |
| 01:50 | 매월 5일 | career `sync-aptitude-meta` | 5초 |
| 01:55 | 매월 4일 | academyinfo `sync-regional-indicators` | 2분 |
| **02:30** | **매일** | **academyinfo `sync-school-indicators --stale-limit 13`** | **74분 → 약 03:45** |
| 04:10 | 매일 | academyinfo `replay-school-indicator-skips --limit 500` | 약 17분 |
| 05:00 | 매월 5일 | academyinfo `sync-startup-support` | 115분 → 약 06:55 |

`--skip-tsv` 는 생략 시 `default_school_indicator_skip_tsv()` 가 자동 적용된다.
replay 1건당 약 2초이므로 `--limit 500` 이면 약 17분이다. `timeout -k 60 1800` 을 건다.

경부하 잡은 전부 02:00 이전에 끝나고, 무거운 두 잡(02:30·05:00)은 서로 겹치지 않는다.
04:10 replay 는 02:30 잡이 정상 종료(03:45)한 뒤에 시작한다.

---

## 5. 컴포넌트 설계

### 5.1 대상 선정 — `load_stale_schools`

신규 CLI 인자 `--stale-limit N`. **`sync-school-indicators` 전용이다.**
`sync-subject-master` · `sync-startup-support` 도 `--school-offset` / `--school-limit` 을
받지만 이번 변경 대상이 아니며 동작이 바뀌지 않는다.

기존 `--school-offset` / `--school-limit` 은 수동 실행·디버깅용으로 존치한다.
`--stale-limit` 과 `--school-offset` / `--school-limit` 을 함께 주면 인자 오류로 종료한다.

```sql
SELECT s.schl_id, s.svy_yr, s.name, s.div_cd
FROM (
    -- 기존 load_schools(scope='latest') 와 동일한 최신연도 서브쿼리
    SELECT s1.schl_id, s1.svy_yr, s1.name, s1.div_cd
    FROM school_list s1
    JOIN (
        SELECT schl_id, MAX(svy_yr) AS max_svy_yr
        FROM school_list GROUP BY schl_id
    ) t ON t.schl_id = s1.schl_id AND t.max_svy_yr = s1.svy_yr
) s
LEFT JOIN (
    SELECT schl_id, MAX(recv_time) AS last_recv
    FROM school_indicator_list GROUP BY schl_id
) i ON i.schl_id = s.schl_id
ORDER BY (i.last_recv IS NULL) DESC, i.last_recv ASC, s.schl_id
LIMIT N
```

미수집 학교가 먼저, 그다음 오래된 순. 동률은 `schl_id` 로 안정 정렬한다.

**인덱스: 추가하지 않는다 (2026-08-05 실측 후 철회).**

설계 시점에는 커버링 인덱스 `(schl_id, recv_time)` 추가를 계획했다. `schl_id_idx (schl_id)`
단독이라 `MAX(recv_time)` 집계에서 행 접근이 발생한다는 이유였다. 실행 직전 테이블 규모를
읽기 전용으로 재보니 전제가 틀렸다.

| 항목 | 실측값 |
|---|---|
| 행수 | 4,922 (data 2MB / index 4MB) |
| 실행계획 | `type=index`, `key=schl_id_idx`, `rows=4922` |
| 소요 | **17.3ms** |
| 실행 빈도 | 1일 1회 |

하루 한 번 17ms 쿼리를 위해 인덱스를 더하면, 기존 4MB 인덱스에 얹는 것에 더해 매
`INSERT ... ON DUPLICATE KEY UPDATE` 마다 유지 비용이 붙는다. 공유 RDS에 DDL을 거는
리스크까지 감안하면 순손실이다. 테이블이 10만 행대로 커지면 재검토한다.

부수 확인: `schl_id` distinct 333 vs 학교 마스터 378 → 45개 학교는 미수집 상태다.
`last_recv IS NULL` 이 최우선 정렬이므로 첫 실행부터 이 45개가 먼저 처리된다.

### 5.2 동시성 가드

```
flock -n /var/www/html/update/.locks/academyinfo-school-indicator.lock
```

락 파일은 `/var/lock` 이 아니라 프로젝트 하위 `.locks/` 에 둔다. `/var/lock`(→ `/run/lock`)은
`drwxr-xr-x root root` 라 ec2-user가 파일을 만들 수 없다(실측: `flock: cannot open lock file
... Permission denied`, exit 66). `.locks/` 는 `.gitignore` 에 추가한다.

- 일일 indicator 잡과 replay 잡이 **같은 락**을 공유한다. indicator 가 초과 실행 중이면
  replay 는 자동으로 건너뛴다.
- `-n` (non-blocking) — 큐잉하지 않고 즉시 포기한다. 대상 선정이 자가 치유형이므로
  건너뛴 분량은 다음 실행이 자동으로 회수한다.
- `timeout -k 60 6000` (100분) 을 보조 안전망으로 유지한다. 예상 74분 대비 여유가 있고
  24시간 간격 대비 충분히 짧다.

### 5.3 429 처리

- `SCHOOL_INDICATOR_429_COOLDOWN` 을 **180초 → 5초**로 낮춘다.
- 429는 기존대로 skip TSV에 기록하고 다음 요청으로 진행한다.
- 신규 인자 `--max-consecutive-skips` (기본 50). **연속 카운터는 요청 1건이라도 성공하면
  0으로 리셋된다.** 학교·endpoint 경계와 무관하게 run 전체에서 하나의 카운터를 쓴다.
  임계값을 넘으면 run을 중단하고 종료 사유를 로그에 남긴다. OpenAPI 장애 시 무의미한
  호출을 막는 장치이며, 정상 상태에서는 발동하지 않는다(단독 실행 시 skip 0건 실측).
- 밀린 skip은 04:10 replay 슬롯이 소화한다.

### 5.4 로그

현재 무제한 append 구조다 (35시간에 7.8MB). `/etc/logrotate.d/nzndb-update` 를 추가한다.

```
/var/www/html/update/academyinfo/logs/*.log /var/www/html/update/career/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    su ec2-user ec2-user
}
```

`*/logs/*.log` 와일드카드 대신 두 경로를 명시했다. `update/` 하위에 다른 디렉터리가
생겼을 때 의도치 않게 회전 대상에 들어가는 것을 막는다. 로그 소유자가 `ec2-user` 이므로
`su ec2-user ec2-user` 로 회전 작업 권한을 맞춘다.

**설치 완료 (2026-08-05).** `logrotate --debug` 로 21개 로그 인식과 euid 전환을 확인했고,
폭주 시절 잔재인 7.5MB `sync_school_indicator_batch.log` 는 `-f` 로 1회 강제 회전해
`.1` 로 분리했다 (`copytruncate` 이므로 무손실). 새 스케줄 첫 실행 로그는 빈 파일에서 시작한다.

---

## 6. 데이터 흐름

```
crond
  └─ flock -n (중복 실행 차단)
      └─ timeout -k 60 6000
          └─ update_academyinfo.py sync-school-indicators --stale-limit 13
              ├─ load_stale_schools()          ← recv_time 오래된 13개 선정
              ├─ for endpoint × school × indctId:
              │     fetch_pages()               ← 429 시 4회 재시도 (기존)
              │       ├─ 성공 → upsert_school_indicator()  → recv_time = NOW()
              │       └─ 429  → record_school_indicator_skip() → skips.tsv
              │                  + sleep 5초, 연속 50건 초과 시 run 중단
              └─ commit_cursor() (학교 단위)

crond (04:10)
  └─ flock -n (같은 락)
      └─ replay_school_indicator_skips()        ← skips.tsv 소화
```

`recv_time` 갱신이 곧 진행 상태 기록이므로, 별도 커서 테이블이 없다.

---

## 7. 에러 처리 · 실패 모드

| 실패 | 동작 | 회복 |
|---|---|---|
| 이전 실행이 아직 진행 중 | `flock -n` 이 즉시 포기 | 다음 날 실행이 stale 순으로 회수 |
| 100분 초과 | `timeout` 이 SIGTERM → SIGKILL | 처리된 학교는 `recv_time` 갱신됨. 나머지는 다음 날 자동 선정 |
| 연속 429 50건 초과 | run 중단, 종료 사유 로그 | skip은 TSV에 기록됨. 04:10 replay 가 재시도 |
| DB 커넥션 실패 | 예외로 종료 | 다음 날 실행이 회수 |
| 학교 수 증가 | 신규 학교는 `last_recv IS NULL` → 최우선 선정 | 자동 |

핵심: **모든 실패 경로가 자가 치유된다.** 어떤 이유로 중단되어도 처리 못 한 학교는
`recv_time` 이 낡은 상태로 남아 다음 실행에서 우선 선정된다.

---

## 8. 검증 (DoD)

**등록 전 (2026-08-04 완료):**
- [x] 단위 테스트 19건 통과 (신규 12건 포함)
- [x] `flock` 이중 실행 테스트 — 두 번째가 exit 1로 즉시 종료
- [x] 인자 검증 4케이스 — `--stale-limit` 와 offset/limit 동시 사용, 타 job 사용, 0 이하, 기존 경로
- [x] `--stale-limit 1` 스모크 — 최오래된 학교 `0000004/2025` 선정, 14개 엔드포인트 적재,
      429 skip 18건 TSV 기록, 락 정상 해제
- [ ] 연속 skip 중단 실발동은 미검증 (단위 테스트로만 확인)

**등록 후 7일 관찰:**
- 일 1회만 실행되었는가
- 1회 소요가 90분 미만인가
- 동시 실행 프로세스가 항상 1개인가 (`ps` 확인)
- 로그에 `Too many connections` 0건인가

**30일 후:**
- `school_indicator_list` 의 전 학교 `recv_time` 이 30일 이내로 갱신되었는가

```sql
SELECT COUNT(*) FROM (
  SELECT schl_id, MAX(recv_time) AS last_recv
  FROM school_indicator_list GROUP BY schl_id
) t WHERE last_recv < NOW() - INTERVAL 31 DAY;
-- 기대값 0
```

---

## 9. 테스트

- `load_stale_schools` 단위 테스트 — 미수집 우선, 오래된 순, `LIMIT` 준수
- `--stale-limit` / `--school-offset` 상호 배타 인자 검증 테스트
- 연속 skip 중단 로직 테스트 (임계값 도달 시 run 중단)

기존 `academyinfo/tests/` 구조를 따른다.

---

## 10. 롤백

기존 크론 라인은 삭제하지 않고 주석으로 보존한다. 문제 발생 시 주석 교체로 즉시 복귀한다.
코드 변경은 서버 git 저장소(`lazenius/nzndb-update`)에 커밋하므로 revert 가능하다.

---

## 11. 범위 밖 — 후속 권고 (별도 승인 필요)

이번 설계에 **포함하지 않는다.** 인프라 변경이므로 별도 판단·승인이 필요하다.

### 11.1 RDS max_connections

RDS MySQL 기본 파라미터 그룹은 수식 `{DBInstanceClassMemory/12582880}` 을 쓴다
(메모리 ÷ 약 12MB). db.t3.micro(1GiB) 기준 약 85, small(2GiB) 약 170 수준이다.

확대하려면 커스텀 파라미터 그룹을 만들어 연결해야 한다(기본 그룹은 수정 불가).
`max_connections` 자체는 동적 파라미터지만, **파라미터 그룹을 새로 연결하는 작업은
재부팅 1회가 필요**하다. Single-AZ면 실제 중단이 발생하므로 야간 창에 해야 한다.

다만 값을 올려도 메모리는 늘지 않는다. 커넥션당 스레드 스택·버퍼를 소비하므로
수식 기준을 크게 초과하면 OOM·스왑 위험이 있다. 인스턴스 클래스와 함께 판단해야 한다.

### 11.2 계정별 커넥션 상한 (더 본질적)

RDS를 여러 사이트가 공유하는 구조라면 총량 확대보다 계정 격리가 핵심이다.

```sql
ALTER USER '<batch_user>'@'%' WITH MAX_USER_CONNECTIONS 5;
```

이번과 같은 폭주가 재현되어도 수집기는 5개까지만 점유하고 그 이상은 자체 실패한다.
웹 사이트는 영향받지 않는다. **이번 장애의 실질적 격벽이다.**

### 11.3 함께 점검할 것

- 수집기 전용 DB 계정 분리 여부 (현재 웹과 동일 계정을 쓰는지 확인 필요)
- PHP 측 persistent connection(`pconnect`) 사용 여부
- `wait_timeout` 축소 (MySQL 기본 28800초 = 8시간)
- CloudWatch `DatabaseConnections` 지표로 실제 피크 확인 후 목표값 산정

---

## 12. 관련 파일

| 경로 | 역할 |
|---|---|
| `academyinfo/update_academyinfo.py` | 수집기 본체 (`sync_school_indicators` 1320행, `replay_school_indicator_skips` 1378행) |
| `academyinfo/include/common.py` | `connect_db`, `fetch_pages` (429 재시도 160행대) |
| `academyinfo/logs/sync_school_indicator_batch.log` | 장애 근거 로그 |
| `academyinfo/logs/sync_school_indicator_skips.tsv` | 429 skip 기록 (08-05 `logs/archive/` 로 이동) |
| 서버 `crontab -l` (ec2-user) | 스케줄 |

---

## 13. 2026-08-05 개정 — 엔드포인트 일일 한도 기반 전량 수집

첫 실실행 점검에서 §1의 원인 분석이 부분적으로 틀렸음이 드러났다. 이 절이 현행 설계다.
서버 커밋 `6316bbd`.

### 13.1 확정된 사실

**429는 버스트가 아니라 OpenAPI 엔드포인트(오퍼레이션)당 일일 1,000회 한도 소진이다.**

로그 실측 — `getComparisonFullTimeFacultyResearchCrntSt` 성공 호출 수:

| 날짜 | 성공 | 429 |
|---|---|---|
| 08-03 | **정확히 1,000** | 5,712 |
| 08-04 | **정확히 1,000** | 5,556 |
| 08-05 | **정확히 1,000** | 48 |

08-05 타임라인: 02:32:12 첫 호출 → 03:24:02 1,000번째 성공 → 03:24:58 첫 429 →
04:10 timeout kill. 자정 리셋은 정상 동작하며, 엔드포인트가 차단된 것이 아니다.

한도를 넘긴 원인은 **indctId 팬아웃**이다. `indctId` 필수 엔드포인트 2개에 `code_list`
`key_indicator` 83개를 전부 곱했다. `13학교 × 83코드 = 1,079 > 1,000` — `--stale-limit 13`
은 설계 시점부터 한도 초과값이었다.

실측 스윕(학교 0000003 / 0000005, 83코드 전량)으로 확인한 유효 코드:

| 엔드포인트 | 유효 indctId | 비고 |
|---|---|---|
| `getComparisonFullTimeFacultyResearchCrntSt` | `66`, `67` | 나머지 81개는 빈 응답 |
| `getComparisonFullTimeFacultyEnsureCrntSt` | `66`, `67` | 동일 |
| `getNoticeFullTimeFacultyResearchCrntSt` | (불필요) | 1콜에 54~60 7건 반환 |

### 13.2 폐기된 §4·§5.1·§5.3

학교당 호출이 40회(비FAN 36 + FAN 2×2)로 줄어, 엔드포인트별 일일 호출이
**최대 754회 / 한도 1,000회(75%)** 가 된다. 전 엔드포인트가 한도 안에 들어오므로
**377개교 전량 매일 수집**이 가능하다. stale 롤링·replay 창은 존재 이유가 사라졌다.

| 항목 | 구(舊) | 현행 |
|---|---|---|
| 대상 선정 | `--stale-limit 13` (`recv_time` 오래된 순) | 전량 377개교 |
| 회전 주기 | 약 30일 | 매일 |
| replay 잡 (04:10) | 별도 슬롯 | **제거** |
| 요청 지연 | 0.6초 / 엔드포인트별 3.0초 | 0.1초 (실측 응답 0.131초) |

### 13.3 신규 안전장치

**엔드포인트별 일일 호출 예산** — `SCHOOL_INDICATOR_ENDPOINT_CALL_BUDGET = 900`
(한도의 90%). 예산으로 전 학교를 못 덮으면 시도가 오래된 학교부터 자르고 나머지는
다음 실행이 이어받는다. 현재는 754 < 900 이라 발동하지 않는 가드다.

**`school_indicator_attempt` 대장** — 08-05 실측된 livelock 해소.
`school_indicator_list.recv_time` 은 행이 적재된 학교만 갱신되므로, 데이터가 없어 0건이
오는 학교는 순번이 영원히 갱신되지 않아 같은 13개교가 무한 재선정됐다(08-05 실제 발생,
당일 적재 0행). 적재 여부와 무관하게 시도 자체를 기록해 회전시킨다.

**엔드포인트 단위 429 서킷 브레이커** — `SCHOOL_INDICATOR_ENDPOINT_429_BREAKER = 5`.
연속 429가 5건이면 해당 엔드포인트만 이번 run에서 포기한다. 한도 소진은 그날 안에
회복되지 않으므로 계속 두드릴 이유가 없다. 08-05 45분 재시도 폭주의 재발 방지.

### 13.4 현행 크론

```
30 2 * * * cd /var/www/html/update/academyinfo && \
  flock -n /var/www/html/update/.locks/academyinfo-school-indicator.lock \
  timeout -k 60 6000 /usr/bin/python3 update_academyinfo.py \
  sync-school-indicators --scope latest >> logs/sync_school_indicator_batch.log 2>&1
```

`--stale-limit 13` 제거. 04:10 replay 잡 삭제(잡 16개 → 15개). flock·timeout 유지.

### 13.5 검증 (08-05 실측)

| 항목 | 결과 |
|---|---|
| 스모크 (학교 0000003, 전 엔드포인트) | 38콜 성공, 43행 적재, 시도 대장 37건 |
| 검증 실행 (20개교) | 760콜 성공 = 20 × 38, 시도 대장 740행 |
| 서킷 브레이커 | 연속 429 5건에서 정확히 발동, 잔여 학교 호출 차단 |
| **전량 실행 (377개교)** | 16:54:44 → 17:54:37, **59분 53초**, `batch completed` |

전량 실행 실측 (`logs/manual_fullsweep_20260805.log`):

| 항목 | 값 | 판정 |
|---|---|---|
| 성공 콜 | **14,326** = 377 × 38 | 이론값과 정확히 일치 |
| 429 | 5 (Research 한정, 당일 한도 소진분) | 브레이커 즉시 차단 |
| 시도 대장 | 13,949행 / **377개교** / 37엔드포인트 | livelock 해소 실증 |
| 적재행 | **14,169** (같은 날 새벽 크론은 0행) | — |
| 적재 학교 수 | 333 → **336** | 신규 3개교 유입 |
| 최대 소비 엔드포인트 | `EnsureCrntSt` **754 / 1,000 (75%)** | 예산 900 적정 |
| 그 외 엔드포인트 | 각 377~378 / 1,000 (38%) | — |

예산 900은 학교 448개까지 수용한다(448 × 2 = 896). 그 이상 늘면 상향 또는
FAN 엔드포인트 제거(§13.1 Notice 대체) 검토.

런타임 59분 53초 중 4분 30초는 Research 브레이커 소진분이다. 크론 실행 시각(02:30)에는
한도가 리셋돼 있어 이 손실이 없는 대신 Research 754콜(약 3분)이 추가되므로 실질 동일하다.

미확인: 크론 경로 자체(02:30 flock 획득, 로그 append)의 정상 동작.
