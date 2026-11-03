> **Windows local launch verified (2026-11-03 KST):** Generated folder now includes RUN_LOCAL_WINDOWS.cmd. From the generated folder execute RUN_LOCAL_WINDOWS.cmd --check to verify installed Python3.11+/FastAPI/Uvicorn without network/install or server startup, then RUN_LOCAL_WINDOWS.cmd to launch fixed 127.0.0.1:8000. The --check does NOT verify database integrity or actual user acceptance. Native Windows+Ubuntu Actions at code SHA 0b62485155b2c93cd73d02a44afc8b42dfffe940: static each OS 167 PASS/2 SKIP, real browser each OS 155 PASS/2 SKIP, all jobs SUCCESS. Product and customer rights remain RELEASE HOLD.

# REA_WEB — 로컬 완성형 앱 생성 (REA 직접 생성 백엔드만)

**현재 단계:** 별도 고객 ZIP 실행 없이 자체 REA 템플릿으로 SQLite+FastAPI+독립 대시보드를 한 폴더에 생성합니다. 원본 데이터·Fable 사용 권한 및 명시적 매핑 승인이 필요합니다. 상용 RELEASE HOLD.

## 한 명령으로 생성

```powershell
python -m rea.adapter.local_product --data .\OWNED.csv --fable .\fable.json --bindings .\samples\rea_firstparty_bindings.json --out .\NEW_LOCAL_APP --owner-authorized-data --owner-confirmed
```

CSV/JSON에 id/title/category 필드가 없으면 기존 REA 명시적 매핑을 JSON 파일로 작성하고 --mapping MAPPING.json을 추가합니다. 이 예제 GET 계약은 실제 REA 소유 템플릿에만 적용합니다. 입력 데이터·Fable JSON과 템플릿은 원본 그대로 보존합니다.

생성되는 NEW_LOCAL_APP에는 읽기 전용 data.sqlite, app.py, static/, dashboard/ (정확히 5파일), requirements.txt, README.md, REA_INTEGRATION_RECEIPT.json 등이 들어 있습니다. 외부 사이트에 접속하거나 고객 제공 백엔드 ZIP을 추출·실행·포함하지 않습니다. 결과는 새 폴더에 원자적으로 발행하며 기존 폴더를 덮어쓰지 않습니다.

## 로컬 실행

```powershell
cd .\NEW_LOCAL_APP
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

브라우저에서 http://127.0.0.1:8000/dashboard/ 는 생성 대시보드, http://127.0.0.1:8000/ 는 기존 REA 로컬 앱입니다. 패키지 설치는 별도 사용자 동작이며 상용 배포·의존성 라이선스 승인과 다릅니다.

## 차단 경계

- 실제 고객 데이터는 자동 처리하지 않습니다. 사용자가 소유·비민감 자료와 법적 권리를 확인한 경우에만 명령을 직접 실행합니다.
- 본 산출물은 REA가 직접 생성한 고정 템플릿에만 유효합니다. 임의 고객 ZIP→실행 앱 변환은 지원하지 않으며 격리 실행·별도 승인 없이 추가하지 않습니다.
- 앱은 loopback 전용이며 외부 접속/로그인/인증/공개 배포를 지원하지 않습니다. 데이터는 파일 data.sqlite에 평문으로 들어갑니다.
- 분리된 고객 보안/권리/프라이버시/지원/Windows 실제 사용자 검증 후 상용 승인해야 합니다. CI 합성 확인은 제품 출시 허가가 아닙니다.
