# update/academyinfo/include

## 용도

- `academyinfo` 수집기 공통 모듈과 서버 전용 설정 파일 위치

## 파일

- `common.py`
  - DB 연결
  - OpenAPI URL 조합
  - XML 파싱
  - raw 저장
- `common_local.py.example`
  - 설정 예시 파일
- `common_local.py`
  - 실제 서버 설정 파일
  - **git 추적 제외**

## 주의

- `common_local.py`에는 다음 값이 들어간다.
  - DB 접속 정보
  - `SERVICE_KEY`
  - 필요 시 `SERVICE_URL`
- 실제 비밀값은 로컬 저장소에 두지 않고 서버에만 유지한다.
