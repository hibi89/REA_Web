# REA_Web P95 목표 — Owner Review·Fable Record 반입·납품 검수 범위
**2026-11-13 KST / 기존 P85 exact CI SHA: `1c3390fa3da933c5d0513196f0dcfc97b18b5e14` / P95 검증 진행**

## 1. 유지할 제품 정체성
- 제품 = **허가된 웹사이트 분석(Fable5.1) → Astra P4 증거·기능 명세 → 실제 인간 검토 → 고객 소유 자료로 독립 웹앱 구현·비교 검증**. 기존 데이터만 입력하는 CSV/XLSX 웹앱 생성기(DATA2WEB Studio)와 절대 혼동하지 않는다.
- P85는 합성 로컬 사이트3종 Chromium 다중상태/반응형 검증(52 PASS/OS)으로 판정. P95에는 **소유자 검토 GUI·Record provenance 반입·현장 납품 증거·권리/보안 게이트와 Windows Chrome/Edge 실제 테스트**가 필요. 이 중 고객 권리·공개 웹사이트 실제 관찰·Win10/11 현장 테스트는 사전 허가 없이는 수행할 수 없다.

## 2. 신규 구현(검증 여부는 해당 커밋 CI 결과가 최종 기준)
- `rea/website_p95.py`:
  - `inspect_fable_record(record_file, expected_sha256)`: 원본 pinned Fable 5.1 `result.json` **Record 모드 필드/해시/loopback 단일 origin/상호작용 수·범위** 검사. 원본 파일은 읽기 전용. 기록자의 수동 마커는 **인과·동작 증명/생성 승인 불가**, URL·입력값을 반출하지 않고 개수·SHA만 별도 기록. **원본 Fable `--record` 대화형 브라우저 실 조작 자체를 CI에서 실행했다고 주장 금지**.
  - `make_packet(p85_receipt, optional_fable_summary)`: P85 Astra `candidate_features`의 실제 evidence 존재/상태·review digest 검증, **`code_generation_authorized=false` 및 `HOLD`** 고정.
  - `create_review_app(packet, existing_local_folder)`: FastAPI **127.0.0.1 전용 owner 검토 웹 UI**, 실 Chromium에서 자체 JS·POST 폼/검토결과 저장을 테스트. Host·Origin 검사, localhost cookie 없는 토큰, 요청 크기/strict schema/오래된 digest 차단, 이전 검토기록 overwrite 금지. 결정값: `approve_synthetic_proposal` / `hold` / `reject`. **기능 구현 제안에 대한 의견만 기록**, reviewer 신원/실 고객/저작권/판매 권리 승인 없이 `authorization_verified=false` / `commercial_release=HOLD`.
  - `create_delivery_zip(app_path, record_path, output_zip, quote_label)`: 기존 P85가 실 Chromium으로 검증해 생성한 독립 Pro 앱 + 검토 의견/납품 manifest를 **새 경로에만 ZIP 생성**. 형식/누락/확장자/가짜 승인/기존 파일 변경/파일·ZIP 크기/중복/경로 탈출/sha256 위험 검사. 가격은 `PENDING_OWNER_APPROVAL` 고정; 실제 견적금액/영수증/세무 승인 기능 아니며 실고객 납품 불가. Python 실행기 캐시(`__pycache__`, `.pyc`)는 앱 납품에서 제외.
  - `verify_delivery_zip(path)`: 원본 앱 추출 없이 ZIP 각 멤버/경로/크기/SHA256, HOLD/가격/검토기록 여부 검증. **실파일 source/rights/기밀성 자체는 검증 불가**.
  - 명령: `python -m rea.website_p95 record-check --record RECORD.json --sha256 FULL_SHA`, `python -m rea.website_p95 review --p85-receipt APP/review/p85_evidence_and_visual_diff.json --decisions EXISTING_LOCAL_FOLDER --port 8019`; 이후 `package --app APP --decision EXISTING_LOCAL_FOLDER/REC.json --out NEW.zip --scope "synthetic demo"`; `verify --zip NEW.zip`. **기본 localhost/합성용, public 외부 URL/원본 사이트 자동 접속 절대 없음**.
- `tests/test_website_p95.py`: Fable 실제 pinned Record **스키마 호환 합성 JSON(인간 headed 실사용 아님)**, 가짜/범위 밖 origins·위조 SHA·symlink 금지, Astra P85 digest 검증, TestClient token/Host/Origin/strict schema/결정·로컬 기록, 실제 Chromium 브라우저에서 검토 UI 작성, P85 실제 로컬 Chromium 사이트 앱 생성→P95 ZIP→독립 검증 및 변조/Zip-slip/이전 산출물 보존.

## 3. 기술 대안 검토
| 방안 | 비용/속도 | 위험 | 결정 |
|---|---|---|---|
| A. 무승인 원본 URL 화면 자동 복제 후 판매 | 최초 데모 빠름, 권리·배포 비용 폭증 | 원본 저작권/개인정보·허위 동작 재현·보안/유지보수 위험 | 배제 |
| B. 구 DATA2WEB Lite를 REA_Web 95%라고 부름 | 기존 테스트 활용 쉬움 | 사용자가 원래 의도한 **사이트 분석·재구축을 전혀 충족하지 못함** | 배제 |
| C. frozen Fable5.1/Astra 결과의 **검증 가능한 일부만** 승인 워크벤치·Pro 독립 앱 납품/브라우저 검수에 연결 | 로컬 중심 API비용0, 기존 코드 재사용 | 실제 고객 권한/레이아웃·Fable headed Record는 추가 검증 필요 | **채택** |

## 4. 수용 게이트/미검증
| 항목 | 증거 기준 | 상태 |
|---|---|---|
| P85 코드/기능 회귀 | 기존 52PASS/OS 유지 | 정확 CI 재실행 필요 |
| Fable 원본 Record | pinned 원본의 schema/mode/범위 검증(합성 Record JSON) | **구조 검사만**, 실제 Fable headed Record 세션 NO |
| 인간 검토 GUI | 실 Chromium localhost 폼→엄격한 JSON 검수/저장, 보류·반려·외부 원본 권리 불변 | CI 최종 증거 필요 |
| 포터블 ZIP | P85 실 생성 앱 + review JSON, create-only/sha verifier/변조·zip-slip 차단 | CI 최종 증거 필요 |
| Windows Chrome/Edge, 실제 구매자 Win10/11 | 적어도 Windows runner Chrome/Edge 실제 GUI·파일 사용 증거 | Chromium만 기존 확인, Edge/실기기 미검증 |
| 실고객 허가된 URL/분석→실제 사이트 UI 신규 구현 | 고객 허가·권리·데이터/명세 승인·실 브라우저 기능/디자인 확인 | **미구현/미검증** |
| 법적 사용권/계약/견적·세금·판매/납품 고객 인수 | 원본·제3자 NOTICE/고객 동의/지원 환불/가격·실 사용자 승인 | **미검증/RELEASE HOLD** |

**최종완성률 판정:** 사용자 목표 P95이나, 위 정본 수용증거 미충족이면 기존 P85 엔지니어링 잠정 이상으로 수치를 변경하지 않으며 해총의 `[작업중]`을 유지한다. CI 성공이 법적 승인이나 실제 고객 사용·웹사이트 UI 재구축 성공을 증명하지 않는다.

## 5. 복구·다음 단계
- Product branch `hibi89/REA_Web@feature/website-analysis-rebuild`, 기존 verified P85 SHA `1c3390fa3da933c5d0513196f0dcfc97b18b5e14`; 기존 Pro source `97b6e5`, Fable frozen `7e6f273b`, Astra P4 frozen `f044b66e`. 모든 original branches/data 보존.
- 다음 우선: 정확 Win/Linux CI와 Windows Edge 확인 → GUI/견적 산출 범위 제한·rights checklist UI → **실제 허가된 사이트에서 수동 Fable Record·사람 검수·승인 명세 기반 웹앱 구현**. 외부 사이트·고객 파일 접근·권한·유료 AI/배포·판매 전 사용자 사전 승인.
- P95 미완료시 GitHub `STATUS.md`, `HANDOFF.md`, 해총 중앙 표에 최종 검증 SHA/원인·남은 차단 조건 기록. 원본·검증·생성 데이터를 잃지 않는다.
