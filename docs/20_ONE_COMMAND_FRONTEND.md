> **2026-11-03 세션 전환 보호 검증:** 목록/지표를 새로 불러오면 이전 상세 요청의 늦은 200/401 응답은 무시하며, 새 목록 성공 시 상세 패널을 초기화합니다. Windows/Ubuntu Chromium 검증 기능 SHA `d477a9dc`, Actions `41631264392` 각 140 PASS/2 SKIP. 실제 고객 로그인·권한 검증은 별도로 필요하며 상용 RELEASE HOLD입니다.

## 2026-11-03 KST — 전체 브라우저 실행 검증 (자체 제작 백엔드)

단일 명령의 실제 생성 결과를 GitHub Actions Windows 2022 및 Ubuntu 22.04 각각에서 localhost FastAPI + Chromium으로 검증했다. 정확한 기능 SHA `d21540e528fcad0ea09ff210a3514237cea5e3af`; `41630317015` 양 OS 각각 **139 PASS/2 SKIP/0 FAIL**, 정적 ZIP `41630317051` 양 OS 각각 **167 PASS/2 SKIP/0 FAIL**. `tests/test_offline_compose_browser.py`가 실행 명령→5개 프론트엔드 파일 생성→테스트 개발자가 별도로 작성한 동등한 FastAPI 소스 실행→실제 브라우저 목록/KPI/검색/상세/401 데이터 초기화/재연결을 검증한다.

```powershell
python -m pytest -q tests/test_offline_compose.py tests/test_offline_compose_browser.py
```

테스트에서 FastAPI를 실행하는 것은 **테스트가 직접 제작한 코드**에만 한정된다. 단일 명령은 여전히 백엔드 ZIP을 import/추출/실행하지 않으며, 고객 원본·인증·라이선스·실제 Windows 사용자 환경 검증을 대체하지 않는다. 독립 설치용 `playwright`, `fastapi`, `uvicorn` 패키지 및 Chromium 설치가 필요하다. 상용 RELEASE HOLD.

# REA_WEB — 오프라인 백엔드 ZIP → 독립 대시보드 한 번에 생성

현재 단계: **검토용 / 동일 출처 GET / 고객 실환경 미검증 / RELEASE HOLD**.

`python -m rea.adapter.offline_compose`는 기존 ZIP 정적 AST 검사, 타입 힌트 검사, 저장된 Fable 1.0 자료, 수동 API 매핑 및 독립 프론트엔드 생성기를 한 명령에 연결한다. 원본 ZIP을 추출·import·실행하거나 외부 사이트에 접속하지 않는다.

## 1. 소유자 승인 후 미리보기

먼저 **해당 ZIP을 로컬에서 정적으로 읽을 권한을 명확하게 확인**해야 한다. 고객/제3자 원본은 별도 사용 승인이 없으면 이 명령의 입력으로 넣지 않는다.

~~~powershell
python -m rea.adapter.offline_compose --backend-zip .\OWNED_BACKEND.zip --fable .\fable.json --owner-authorized-source
~~~

미리보기는 선언된 GET 후보 경로, 미해결 선언 수 및 원본 해시를 요약하고 `OWNER_REVIEW_REQUIRED`를 반환한다. 실행 가능한 API나 실제 응답 스키마는 검증하지 않는다.

## 2. 수동 필드 매핑

고객이 승인한 **정확한** 3개 GET 경로와 JSON 응답 필드에 한해 `bindings.json`을 작성한다. 아래는 **자체 제작 예제**이며 추론된 실제 고객 필드가 아니다.

~~~json
{
  "list":{"path":"/api/jobs","field":"items"},
  "metrics":{"path":"/api/metrics","field":"__root__"},
  "detail":{"path":"/api/jobs/{job_id}","field":"__root__"}
}
~~~

비표준 JSON 필드가 있으면 기존 `presentation` 맵을 사용한다. 동적 또는 mount 미확인 라우트와 POST/PUT/DELETE는 허용되지 않는다.

## 3. 명시적으로 승인된 매핑만 프론트엔드로 생성

~~~powershell
python -m rea.adapter.offline_compose --backend-zip .\OWNED_BACKEND.zip --fable .\fable.json --bindings .\bindings.json --out .\NEW_FRONTEND --owner-authorized-source --owner-confirmed
~~~

`NEW_FRONTEND`는 존재하지 않아야 하며 덮어쓰지 않는다. 산출물은 `index.html`, `style.css`, `app.js`, `manifest.json`, `README_KO.md` 5개 **프론트엔드 전용** 파일이다. 백엔드 Python, DB, 고객 ZIP, 인증 비밀은 포함하지 않는다.

실제 작동은 신뢰할 수 있는 운영자가 FastAPI의 같은 origin에서 `/dashboard/` 및 정확한 GET `/api/*`를 제공한 뒤 별도 검증해야 한다. 이 절차는 백엔드 서버를 구동하지 않으며, 데이터·인증·권리·라이선스·공급망·격리·Windows 실기·배포를 승인하지 않는다.

## 안전·제약

- `--owner-authorized-source`: 정확한 로컬 ZIP 정적 검사에 관한 **사용자의 명시적 확인 플래그**. 법적 권리의 기술적 증거는 아니다.
- `--owner-confirmed`: 사용자가 제공한 3개 GET/필드 매핑으로 **프론트엔드 소스만** 생성한다. `--bindings` 및 `--out` 동시 필수.
- 검토용 실패나 승인 없는 경우 출력 디렉터리를 만들지 않는다.
- Fable 결과와 선택적 `--visual`은 사전에 정당하게 획득한 JSON으로 제한한다. 본 CLI는 URL을 방문하지 않는다.
- 고객 원본 ZIP 실행, 실제 API 인증, Docker/VM 검증, 외부 업로드, Production/Vercel 배포는 개별 사전 승인 없이는 하지 않는다.

자체 제작 예제 테스트: `python -m pytest -q tests/test_offline_compose.py`. 결과는 synthetic offline 단계에 한정하며 상용 출시 허가는 **RELEASE HOLD**다.
