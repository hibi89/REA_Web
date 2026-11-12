# REA_Web — P85 로컬 합성 브라우저·반응형·증거·보안 검증 (2026-11-13 KST)

## 0. 정확 판정
- **제품은 원래 REA_Web 웹사이트 분석·재구축 엔진**이다. 이 문서의 **엔지니어링 85% 잠정**은 정본 `docs/ORIGINAL_FINAL_DESIGN.md`의 **70→85 수용 게이트(합성 사이트 2+ 영역/다중 상태·반응형·negative/security·source/visual difference report·Windows/Linux CI)**를 검증했다는 내부 단계적 평가다. 실제 임의 사이트의 전체 코드·디자인·업무 동작을 85% 자동 복원했다는 주장은 **거짓**이다.
- **검증 코드·workflow 정확 SHA:** `1c3390fa3da933c5d0513196f0dcfc97b18b5e14`; author/committer `hibi89` 계정 연결 확인.
- **[GitHub Actions #43273324679](https://github.com/hibi89/REA_Web/actions/runs/43273324679)**: **2/2 SUCCESS**, Ubuntu 24.04 **52 PASS·0 FAIL·1 WARN**, Windows Server 2025 **52 PASS·0 FAIL·1 WARN**, `2026-11-12T17:50 UTC` 완료(2026-11-13 KST). 정확 동일 SHA가 실행·테스트된 근거다.
- 실행 명령: `python -m pytest -q tests/test_website_rebuild_p50.py tests/test_website_p70.py tests/test_website_p85.py tests/test_orchestrator.py`. Github Actions의 Python 3.11, Chromium, Pillow, requests/bs4, FastAPI/uvicorn/httpx, pydantic, pytest와 고정 Fable/Astra import checkout 사용.
- 기존 P70 **41 PASS** + P85 추가 테스트 **11개**. 정확 CI 실행 전체 52 PASS, 사용자의 Windows10/11 PC 실기기·Chrome/Edge 추가브라우저는 **NOT RUN**.

## 1. 구현 파일 및 실제 데이터 흐름
- `rea/website_p85.py`: 3가지 자체 제작 합성 업무 사이트(catalog/inventory/directory)를 단일 `127.0.0.1` fixture 서버에서 실제 Playwright Chromium으로 분석. **데스크톱 1280×720 + 모바일 390×844** 각각의 화면에서 순차적으로 **검색 → 카테고리 필터 → 상세 선택**(3동작, 4상태)을 실제 조작하고 DOM before/after와 PNG 캡처/바이트 SHA 기록.
- `tests/test_website_p85.py`: 각 업무 사이트별 실 Chrome 동작·Astra 모델·Pro 앱 비교 3건, 소유자 승인/CSV SHA 위조·review digest 위조·기존 폴더 덮어쓰기·외부 URL 마커·참고 HTML 변조·symlink 등 보안 실패 8건. 기존 P70 코드 및 테스트를 변경하지 않고 확장.
- P85 `inspect_p85`는 최신 실제 실행 결과에 대한 보수적 evidence bundle 생성. Astra P4 고정 원본 `ObservationBundle/derive_spec`로 **뷰포트별 3개의 observed candidate**(총 6개)와 전·후 screenshot Evidence 8개를 실제 모델에서 검증. `approval_gates[].status=pending`, `candidate_features[].review_status=requires_review`, `implementation_ready=false` 유지.
- `build_p85`는 **사전 참조 파일 SHA / 고객 CSV SHA / 전 단계 review digest / `APPROVE_SYNTHETIC_ONLY` / 명시 `YES_LOCAL_FIXTURE`**을 재검증한 뒤 P50 경로의 **실제 원형 Fable 5.1 정적 scan.py 1회 루프백 관찰→Astra P4 기술 검토→기존 Pro FastAPI/SQLite 독립 앱 생성**을 수행한다. 생성된 실제 앱도 2개 화면에서 3단계 상태변화를 직접 비교한다. **Fable 5.1의 `--record`를 실행했다고 주장하지 않는다**; 행동 관찰은 별도 P85 Playwright observer가 수행했다.
- UI 기능상태는 각 viewport의 `#count`, `#search`, `#category`, `#detail`를 직접 검사. `3건`→검색 `1건`→필터 유지 `1건`→상세 `커피`가 참고 synthetic과 새 앱 양쪽에서 동등하다고 판정.
- UI·디자인은 동일하지 않다. 실제 스크린샷을 Pillow로 동일 해상도에서 RGB 채널별 절대 차이로 수치화하고, 문서/manifest에는 **`VISUAL_DIFFERENCE_REQUIRES_HUMAN_REVIEW`/ `UNVERIFIED_DIFFERENCE_REPORTED`**로 저장한다. 소스 구조(nav/heading/form control) 개수도 나란히 기록하지만 **디자인·픽셀 동등성이라고 결론 내리지 않는다**.
- 출력은 기존 `rea.safe_publish.publish_directory`의 create-only 원자 게시를 사용; target 존재/변조·위조 허가·외부 네트워크 접속 마커·객체/iframe 입력 거부. 소스 원본 불변; 스크린샷·Astra 증거는 비서비스 `review/p85_evidence_and_visual_diff.json` 및 PNG로만 출고하고, 프로덕션 Public 사이트에 게시하지 않는다.
- 보안 관찰: 로컬 외 도메인/승인되지 않은 경로는 Playwright route abort. fixture는 URL 마커/외부 문서 삽입을 금지, 네트워크 0 대외 요청. 민감 데이터가 reference PNG에 포함될 수 있으므로 실고객 입력/공유에 확대 적용 전 권한/보관·삭제 정책 별도 승인 필요.

## 2. 실패 이력·복구
- 최초 P85 SHA `e0cddf5c59208ae03395fa8d96f00e25c04c5659` [Actions #43273113196](https://github.com/hibi89/REA_Web/actions/runs/43273113196)은 Ubuntu/Windows FAIL. Ubuntu **49 PASS / 3 FAIL**; 오류는 `rea/website_p85.py`에서 검토 보고서의 딕셔너리 `reviewed` 대신 출력 `Path`인 `review`를 `json.dumps`에 전달한 것(`TypeError: PosixPath is not JSON serializable`). 기능/시각 비교 자체의 실패가 아니라 **최종 증거 보고서 직렬화 실패**.
- 최소 수정은 `json.dumps(reviewed, ...)` 한 줄. 기존 소스 보존, 전체 테스트 동일 명령 재실행하여 위의 정확 SHA `1c3390f`에서 **양 OS 52 PASS/0 FAIL**, GitHub 2/2 SUCCESS. 실패 반복·무의미한 워크플로 재배포 없음.
- 이전 P70 검증 `bfac1116ac7a20c7162f42a59e51277d402b24d9`는 별도 재현 baseline, 부모 Pro 기능 `feature/d27-windows-python-discovery@97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d`, 고정 Fable5.1 `7e6f273b359b207fad8f92016226e3058cbcb839`, Astra P4 `f044b66e799289a5a353fdb9cbfdb324e683ffa3` 보존. Git SHA 복구 가능.

## 3. 남은 실제 업무의 단절점
- P85 현 제품은 **합성 사이트/기능이 제한된 카탈로그 Pro 생성기를 실제 브라우저로 검사하는 연구·개발 제품**이다. 실제 외부 URL의 전체 페이지 흐름, 원 Fable Record 네트워크/행동 원본 증거, 사용자 승인형 업무 명세 GUI, 자동 UI/레이아웃의 구조적 재구축·복잡한 workflow, 접근성 전수/Edge/실 고객/상용권 등은 미구현 또는 **NOT VERIFIED**.
- 참고 사이트 스크린샷·고객 데이터나 인증 권한을 외부 송신하지 않았다. 현 자동 검증의 `APPROVE_SYNTHETIC_ONLY`은 실제 사람·고객의 법적 허가가 아닌 명시적인 합성 시뮬레이션 값이다.
- 단계적 완성률 **85% 엔지니어링 잠정**, 판매 가능 여부/실서비스 기능성으로 오인 금지. **RELEASE HOLD, 실제 사용자 서비스·Vercel/Production N/A**. 정확 기능/QA 신뢰 경계는 사용자 승인 후에도 재검증 필요.

## 4. 다음 단계/관리
- 사용자 다음 목표가 P95일 경우 우선 **실제 Fable Record→Astra 요구/검토→인간 UI 승인→고객 권리·데이터 기반 별도 앱 구조 재설계**에 집중. Windows10/11 Chrome·Edge 실제 사용자 PC 검증, 원본 사용권·NOTICE·고객 data/PII/지원·환불 승인 전 판매 NO-GO.
- 해총 `hibi89/hackathon-command-center-2026@kmong-productization` 중앙 활성상품 명부에서 REA_Web 본품 70→85% 잠정으로 갱신하고 **현재 P85 목표 달성에 따라 해당 [작업중]만 제거**. 다른 상품/표식·DATA2WEB 점수 손대지 않음.
- 갱신: **2026-11-13 KST**, GitHub Actions #43273324679 실증 SHA 기준. 이 문서나 STATUS/HANDOFF 이후 새 커밋은 검증 실행 SHA와 별도로 추적.
