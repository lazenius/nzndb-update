# 구현 갭 요약

## 기준

- 세부 상태표:
  - `career/SERVICE_SPEC_STATUS.md`
  - `academyinfo/SERVICE_SPEC_STATUS.md`
- 이 문서는 **미구현/부분구현만 빠르게 확인**하기 위한 요약이다.

---

## Career

### 부분구현

| 대상 | 현재 상태 | 다음 작업 |
|---|---|---|
| 학교 정보 6개 스펙 (`elem_list`, `midd_list`, `high_list`, `univ_list`, `seet_list`, `alte_list`) | `school_list` 테이블과 구형 `update_school.py`는 있으나, `update_career.py` 통합 엔트리포인트/cron에는 미편입 | `sync-school-list` 명령 추가, 소스 파싱/DB upsert를 통합 수집기로 이관 |
| 학과 정보 2개 스펙 (`high_list`, `univ_list`) | `subject_list` 테이블과 구형 `update_major.py`는 있으나, `update_career.py` 통합 엔트리포인트/cron에는 미편입 | `sync-subject-list` 명령 추가, 구형 스크립트 로직 통합 |
| 직업 상세 확장 테이블 일부 | `job_work_list`, `interest_list`, `research_list`, `job_ready_list`, `forecast_list`, `perform_list`, `ability_list`, `depart_list`, `tag_list`, `job_rel_org_list`는 반영됨 | `edu_chart`, `major_chart`, `rel_sol_list`, `certi_list`, `rel_video_list`, `aptitude_list`, `rel_jinsol_list` 등 나머지 상세 테이블 반영 여부 결정 및 구현 |
| 적성/진로심리검사 API (v1/v2) | API 존재 확인, 스펙 문서화만 완료 | DB 적재형인지 실시간 연동형인지 먼저 결정 |

### 미구현 또는 미확정

| 대상 | 상태 | 비고 |
|---|---|---|
| 적성검사 DB 저장 정책 | 미정 | 전용 API는 확인됐지만, 답변/결과 저장은 개인정보·민감정보 검토 필요 |
| 학과 상세 계열 | 미정리 | `update_major_view.py`에 탐색 흔적은 있으나 정식 수집 스펙/테이블로 확정 전 |

---

## Academyinfo

### 부분구현

| 대상 | 현재 상태 | 다음 작업 |
|---|---|---|
| `getCodeBySeriesSystem` | 현재 `raw` 우선 보관, DB 정규화 미확정 | 코드 체계 컬럼 설계 후 `code_list` 또는 별도 테이블 적재 확정 |
| 산학협력 7개 스펙 | `startup_support_list` key-value 1차 적재 기준 | 실제 응답 기준 컬럼 정규화 후 테이블 재설계 여부 결정 |

### 미구현 또는 후속검토

| 대상 | 상태 | 비고 |
|---|---|---|
| 산학협력 정규화 스키마 | 미확정 | 현재는 임시 적재만 존재 |
| 지역/학교 지표 후처리 정규화 | 미확정 | 현재 `val1~val10`, `field_val1~7` 구조 유지 |
| 학교/학과 마스터 배치 최적화 | 부분완료 | `sync-subject-master`는 배치 옵션 추가됐지만 전체 운영 최적화는 계속 필요 |

---

## 우선순위 제안

1. `career` 학교/학과 수집을 `update_career.py` 통합 엔트리포인트에 편입
2. `career` 상세 확장 테이블 중 실제 필요한 것만 선별 구현
3. `academyinfo` 산학협력 7개 API 정규화 여부 결정
4. `academyinfo` `getCodeBySeriesSystem` 저장 정책 확정
