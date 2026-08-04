# academyinfo 수집 크론 재설계

- 작성일: 2026-08-04
- 대상: 서버 `/var/www/html/update` (academyinfo, career 수집 크론)
- 계기: 2026-08-03 ~ 08-04 RDS 커넥션 고갈 및 사이트 접속 장애

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

또한 단독 실행이던 offset=0 배치의 skip은 0건이었다. **429는 중첩의 결과지 원인이 아니다.**
직렬화만으로 429 대부분이 사라질 것으로 본다.

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

**인덱스:** `school_indicator_list` 에 커버링 인덱스 `(schl_id, recv_time)` 추가.
현재는 `schl_id_idx (schl_id)` 단독이라 `MAX(recv_time)` 집계에서 행 접근이 발생한다.

### 5.2 동시성 가드

```
flock -n /var/lock/academyinfo-school-indicator.lock
```

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
/var/www/html/update/*/logs/*.log {
    daily
    rotate 14
    compress
    missingok
    notifempty
    copytruncate
}
```

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

**등록 전:**
- `--stale-limit 1` 스모크 실행 1회. 선정 학교가 실제로 `recv_time` 최소인지 확인.
- `flock` 이중 실행 테스트 — 두 번째가 즉시 종료되는지 확인.

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
| `academyinfo/logs/sync_school_indicator_skips.tsv` | 429 skip 기록 |
| 서버 `crontab -l` (ec2-user) | 스케줄 |
