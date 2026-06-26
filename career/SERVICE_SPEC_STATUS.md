# Career 서비스/스펙/DB/수집기 상태

## 기준

- 기준 문서: `career/DB_SCHEMA.md`, `career/IMPLEMENTATION_SCOPE.md`, `career/COLLECTION_PLAN.md`
- 기준 코드: `career/update_career.py`, `career/update_code.py`, `career/update_jobs.py`, `career/update_school.py`, `career/update_major.py`
- 상태 표기:
  - `예` = 현재 기준 저장소/서버에서 구축 또는 개발됨
  - `부분` = 구형/보조 스크립트 수준 또는 임시/부분 구현
  - `아니오` = 아직 없음

## 서비스 요약

| 서비스 | 스펙 수 | 관련 DB | DB 구축여부 | 수집프로그램 개발여부 | 비고 |
|---|---:|---|---|---|---|
| 코드 마스터 | 3 | `code_list` | 예 | 예 | `sync-code-list`로 운영 |
| 직업 목록/상세 | 2 | `job_list`, `job_work_list`, `interest_list`, `research_list`, `job_ready_list`, `forecast_list`, `perform_list`, `ability_list`, `depart_list`, `tag_list`, `job_rel_org_list` | 예 | 예 | `sync-job-list`, `sync-job-detail` 운영 |
| 학교 정보 | 6 | `school_list` | 예 | 부분 | 구형 `update_school.py`만 있음, 통합 엔트리포인트 미편입 |
| 학과 정보 | 2 | `subject_list` | 예 | 부분 | 구형 `update_major.py`만 있음, 통합 엔트리포인트 미편입 |
| 적성/진로심리검사 API | 5 | 미정 | 아니오 | 아니오 | DB 적재형이 아니라 실시간 연동형일 가능성 높음 |

## 스펙별 상태

| 서비스 | 스펙 | 관련 DB | DB 구축여부 | 수집프로그램 개발여부 | 근거 |
|---|---|---|---|---|---|
| 코드 마스터 | `themes.json` | `code_list` | 예 | 예 | `career/update_career.py` `sync-code-list` |
| 코드 마스터 | `aptds.json` | `code_list` | 예 | 예 | `career/update_career.py` `sync-code-list` |
| 코드 마스터 | `jobcodes.json` | `code_list` | 예 | 예 | `career/update_career.py` `sync-code-list` |
| 직업 목록 | `jobs.json` | `job_list` | 예 | 예 | `career/update_career.py` `sync-job-list` |
| 직업 상세 | `job.json` | `job_list`, `job_work_list`, `interest_list`, `research_list`, `job_ready_list`, `forecast_list`, `perform_list`, `ability_list`, `depart_list`, `tag_list`, `job_rel_org_list` | 예 | 예 | `career/update_career.py` `sync-job-detail` |
| 학교 정보 | `elem_list` | `school_list` | 예 | 부분 | `career/update_school.py` 구형 스크립트 |
| 학교 정보 | `midd_list` | `school_list` | 예 | 부분 | `career/update_school.py` 구형 스크립트 |
| 학교 정보 | `high_list` | `school_list` | 예 | 부분 | `career/update_school.py` 구형 스크립트 |
| 학교 정보 | `univ_list` | `school_list` | 예 | 부분 | `career/update_school.py` 구형 스크립트 |
| 학교 정보 | `seet_list` | `school_list` | 예 | 부분 | `career/update_school.py` 구형 스크립트 |
| 학교 정보 | `alte_list` | `school_list` | 예 | 부분 | `career/update_school.py` 구형 스크립트 |
| 학과 정보 | `high_list` | `subject_list` | 예 | 부분 | `career/update_major.py` 구형 스크립트 |
| 학과 정보 | `univ_list` | `subject_list` | 예 | 부분 | `career/update_major.py` 구형 스크립트 |
| 적성/진로심리검사 API(v1) | `GET /inspct/openapi/test/questions` | 미정 | 아니오 | 아니오 | `career/APTITUDE_API_SPEC.md` 참고 |
| 적성/진로심리검사 API(v1) | `POST /inspct/openapi/test/report` | 미정 | 아니오 | 아니오 | `career/APTITUDE_API_SPEC.md` 참고 |
| 적성/진로심리검사 API(v2) | `GET /inspct/openapi/v2/tests` | 미정 | 아니오 | 아니오 | `career/APTITUDE_API_SPEC.md` 참고 |
| 적성/진로심리검사 API(v2) | `GET /inspct/openapi/v2/test` | 미정 | 아니오 | 아니오 | `career/APTITUDE_API_SPEC.md` 참고 |
| 적성/진로심리검사 API(v2) | `POST /inspct/openapi/v2/report` | 미정 | 아니오 | 아니오 | `career/APTITUDE_API_SPEC.md` 참고 |

## 메모

- `career/update_career.py` 기준 운영 대상은 현재 **코드 + 직업 목록 + 직업 상세**까지다.
- `school_list`, `subject_list` 테이블은 스키마/구형 수집 스크립트가 있으나, 현재 cron/통합 엔트리포인트 기준으로는 아직 운영 편입 전이다.
- 적성검사 API는 별도 존재하지만, 현재는 **DB 구축 전 스펙 문서화 단계**다.
- `career/DB_SCHEMA.md`에는 장래 확장 테이블(`edu_chart`, `major_chart`, `rel_sol_list` 등)도 있으나, 현재 통합 수집기 기준으로는 이 문서에서 제외했다.
