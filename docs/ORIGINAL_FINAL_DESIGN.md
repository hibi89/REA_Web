> **2026-11-13 KST P85 단계 수용·설계 본문 불변:** 합성 업무 사이트 catalog/inventory/directory 3종 데스크톱·모바일 실 Playwright Chromium 검색→필터→상세 연속 상호작용, 실제 Astra P4 observed/evidence + approval pending, 기존 pinned Fable5.1 정적 scan→승인 합성 CSV 기반 Pro 독립 앱 생성·기능 비교, screenshot RGB 차이/DOM report·XSS/외부 URL·SHA/덮어쓰기 차단 테스트. [정확 GitHub SHA 1c3390fa... CI #43273324679](https://github.com/hibi89/REA_Web/actions/runs/43273324679) Windows/Ubuntu 각 52PASS/0FAIL, 2/2 SUCCESS. 정본 70→85 **합성/다중 상태/반응형·보안·시각차이 비교 게이트 = 엔지니어링 85% 잠정**. 원래 사이트 디자인 복원 자동화 성공/실 외부 사이트·고객/법적 사용권/Production **NOT VERIFIED, RELEASE HOLD**. 이전 70%·UNASSESSED는 작성 시점 역사 상태. [정확 범위 보고](https://github.com/hibi89/REA_Web/blob/feature/website-analysis-rebuild/docs/WEBSITE_P85_RESPONSIVE_ACCEPTANCE_20261113.md).

> **2026-11-13 KST P70 최신 수용 상태(설계 본문은 원형 보존):** 원래 REA_Web 로컬 합성 HTML 사이트 3종의 실제 Chromium 검색/필터/상세 관찰→실 Astra P4 observed 증거/보류→별도 승인 합성 CSV 기반 기존 Pro 웹앱 생성→동작 결과 비교를 [정확 소스 SHA bfac1116 CI #43266467950](https://github.com/hibi89/REA_Web/actions/runs/43266467950)로 Windows/Linux 각 41 PASS, 2/2 SUCCESS 확인. 단계표 50→70 수용을 **엔지니어링 70% 잠정**으로 판정. Fable은 P50의 실제 정적 스캔, 브라우저 행동은 별도 Playwright observer, 자동 디자인 복제/실 외부 사이트·고객/저작권·상용 검증은 불가·미검증, RELEASE HOLD. 이전 아래 UNASSESSED/NOT RUN은 2026-11-12 기준 역사적 기록. [상세 검증](https://github.com/hibi89/REA_Web/blob/feature/website-analysis-rebuild/docs/WEBSITE_P70_BROWSER_ACCEPTANCE_20261113.md).

# REA_Web — 원래 웹서비스 분석·재구축 엔진 최종설계 v1.0
**2026-11-12 KST 사용자 재확정 정본 / 판매·배포 RELEASE HOLD**

## 0. 절대 바뀌지 않는 정체성
REA_Web은 **기존 웹사이트를 분석해 구조·화면·기능·사용 흐름을 증거로 기록하고, 고객의 명시적 권한과 데이터로 별도의 웹서비스를 설계·구현·검증하는 플랫폼**이다. 참고 웹사이트 화면을 넣고 AI가 단순히 CSV 차트를 그리는 제품이 아니다.

사용자 결정: REA_Web의 원래 목적을 되살리고, 기존 REA Lite/CSV·JSON 오프라인 HTML 생성 기능은 **독립 저장소 `hibi89/data2web_studio`**로 제품화한다. 기존 REA_Web의 Pro 코드·기술 샘플·Fable/Astra 원본 브랜치를 삭제하거나 새 제품으로 덮어쓰지 않는다.

## 1. 100% 최종 제품의 사용자 경험
1. 사용자가 분석 권한을 가진 참고 사이트 URL/스크린샷/HTML/사용자 제공 녹화와 원하는 기능·브랜드·사용 시나리오를 **입력 및 승인**한다.
2. URL/수집범위/허용 페이지·동작·계정과 로그인·robots/ToS·속도/기간·PII 마스킹이 명시된 **측정 계획**을 생성하고 소유자가 승인한다.
3. Fable 5.1이 허용된 사이트의 **브라우저 렌더링·레이아웃·UI 컴포넌트·탐색 흐름·반응형 동작·접근성·상태 변화**를 관찰한다. 정적 스냅샷/DOM/사용자 제공 영상도 분석 입력이 될 수 있으나 관찰하지 않은 인터랙션은 추정으로 표시한다.
4. Astra가 관찰증거의 **출처, 타임스탬프, 페이지/selector, 스크린샷, DOM/API 사실 여부, SHA**, 신뢰도와 누락을 저장하고 기능·화면·데이터 계약 명세를 만든다.
5. 엔진은 UI/기능 요구사항·API/DB/권한·디자인 토큰과 구현 불가능/추정 사항을 구분해 제안한다. **검토·수정·보류·승인**을 인간이 결정하며 자동 추측을 사실로 승격하지 않는다.
6. 승인된 요구사항과 고객 **소유 데이터**(CSV/JSON 또는 명시적 매핑/별도 어댑터)로 **독립적인 웹앱**을 생성한다. 원본 사이트의 코드를 복사하지 않고 본인이 설계한 템플릿·컴포넌트·기능계약을 새로 구현한다.
7. 생성된 앱을 참고 사이트의 **관찰된 범위**와 기능·화면·반응형·키보드/접근성·네트워크·보안·데이터정합성 기준으로 재검증한다. 차이가 나면 evidence-linked change request를 생성해 재구현하거나 HOLD한다.
8. 고객에게 원본 사이트/데이터 출처와 실제 새 앱 소스·테스트 보고·README/설치 ZIP·검수 영수증을 전달한다. 납품·판매/운영배포는 별도 고객·권리·보안/인수 승인 후에만 한다.

## 2. 범위와 금지
**지원 목표:** 정적·일반 공개 HTML부터 제한된 공개 사이트 상호작용, 페이지 구조/흐름/레이아웃 관찰, 고객 소유 데이터 기반 카탈로그·예약/목록·폼 등 안전한 한정 기능의 신규 웹앱. 사이트 구조 분석에 한정된 경우 재구축 없이 분석 보고서만 납품할 수 있으나 이것은 하위 서비스이며 전체 제품 대체가 아니다.

**제외/명시 승인 필요:** 무단 크롤링·robots/ToS 우회, CAPTCHA·접근 통제 우회, 인증이 필요한 타인의 시스템에서 권한 없는 데이터 추출, 원본 JS·CSS·이미지/상표·상업 컨텐츠 무단 복제, 숨겨진 서버 로직 추출 주장, 고객의 운영 DB 직접 조작, 결제/계정/보안 권한 변경, 프로덕션 배포, 정확 픽셀 복제 보증. 원본 screenshot과 Fable/Astra 추정 결과를 실행 가능한 원본 코드로 가장하지 않는다.

## 3. 설계 대안
| 접근 | 구현 속도 | 비용·외부 API | 품질/권한 | 판단 |
|---|---|---|---|---|
| A. URL만 받아 화면 자동 복제 | 데모 빠름 | 브라우저·모델 호출 변동 | ToS/저작권·디자인/동작 왜곡·무단 수집 위험 | 배제 |
| B. 현재 CSV·JSON/정적 HTML 생성기만 상품 본체로 사용 | 빠른 납품 | 최저 | **사이트 분석 본래 요구를 충족 못함** | DATA2WEB로 분리 |
| C. **권한 승인형 Fable 관찰 → Astra 증거/명세 → owner 검토 → 독립 앱 생성 → E2E 재검증** | 단계적 | 브라우저 로컬 기본, AI 호출 사용량 상한 | 사실과 추정·권리·설계를 분리, 장기 확장 가능 | **채택** |

기존 Pro의 FastAPI/SQLite/생성·보안·배포 코어는 C의 **실제 구현 어댑터**로 재사용한다. **Fable→Astra evidence adapter**는 이미 단독 합성 경로가 있지만 실사이트 종단 결합 여부는 별도 검증 대상.

## 4. 도메인·모듈 설계
```text
  Authorized Customer Input (URL/screens/video/HTML/requirements/customer data)
       │ consent + scope + rate/PII/CSP/license gate
       ▼
  Fable 5.1 Observation Adapter ── screenshot / DOM / interaction / states
       │ SOURCE, EVIDENCE, UNKNOWN strictly separated
       ▼
  Astra P4 Evidence + Requirements Mapper
       │ evidence ledger / findings / confidence / conflicts / limitations
       ▼
  Human Approval Workbench (HOLD / APPROVE / EDIT / REJECT)
       │ approved functional/UI/data/security contract
       ▼
  REA Pro Independent Builder (FastAPI + SQLite + JS / template renderer)
       │ no source-cloning, use customer-approved data only
       ▼
  Synthetic + Authorized Browser E2E / regression / security / diff
       │ actual UI, DOM, function and data parity limited to observed scope
       ▼
  Deterministic Delivery ZIP + Checksums + license/rights ledger
       │ SELLER / CUSTOMER / LEGAL RELEASE GATE
       ▼
  Approved Delivery or RELEASE HOLD
```

**분리 계층:**
- `site_observer`: 명시 범위/세션·출력 제한, network/capture evidence; 입력은 allowlist 중심, 무단 접근 배제.
- `fable_bridge`: 원본 Fable 5.1의 지원하는 관찰 포맷 정규화, 미지원 포맷은 HOLD.
- `astra_bridge`: partial P4 contract의 실제 검증 가능한 필드만 채택; confidence 허위 생성 거부.
- `evidence_store`: SHA/URL/selector/screenshot reference + observed/inferred/not-observed + retention; 고객 비밀/개인정보를 무단 저장하지 않음.
- `spec_workbench`: 기능·화면·디자인 토큰·데이터 계약과 테스트 조건, 반드시 인간 승인 기록.
- `app_builder`: 기존 `rea/mvp.py`, `rea/orchestrator.py`, `rea/templates`를 기반으로 독립 웹앱 생성; Fable 결과로 원본 코드 추출 불가.
- `app_validator`: 브라우저 가시 기능+접근성+네트워크+security+SHA provenance.
- `delivery`: create-only ZIP, 원본/출력/검증 manifest, 독립 QA, 실패/중복/경합 안전.

**코드 분리 원칙:** DATA2WEB에서 필요한 기존 Lite parser·템플릿의 독립 소유권 정리만 수행; 현재 REA_Web main/Pro의 라이브 코드/브랜치 변경 없이 별도 리포에서 마이그레이션. REA_Web은 기존 Pro 기능을 폐기하지 않고 사이트-분석 상위 계층을 구현한다.

## 5. 데이터 계약과 보안
### 원본 관찰 증거(JSON 예시)
```json
{
  "site_ref": "authorized.example",
  "observation_id": "sha256:...",
  "page_path": "/authorized-page",
  "observed_at": "ISO-8601",
  "claim_level": "observed|inferred|unknown",
  "source_kind": "browser|dom|screenshot|user-video",
  "source_sha256": "<SHA256>",
  "findings": [],
  "pii_redacted": true,
  "owner_scope_approved": false
}
```
- 예시는 계약만 설명하는 **가상값**. 원 URL/도메인·고객 PII/실 크롤링 로그를 GitHub에 적재하지 않는다.
- 재방문 시 동일 승인 범위·경로·증거 해시 확인. 네트워크나 브라우저 장애가 나면 종전 관찰을 최신으로 착각하지 않고 `NOT_VERIFIED/HOLD`로 종료.
- 권한: 고객은 **참고 사이트 관찰 허가 + 콘텐츠 권리 + 본인 데이터 사용권**을 각각 명시. public 웹사이트가 곧 전체 콘텐츠 복제권은 아니다.
- API 한도: 브라우저 세션·페이지 수·스크린샷 크기·모델 토큰/원화 비용을 실행 전에 설정, 캐시된 증거 SHA가 일치하면 재관찰 여부 결정. 무한 재시도·자동 결제 금지.
- 상태 저장/조회: 증거는 append-only, 승인된 spec과 생성물은 버전별 저장; 읽기 쿼리와 쓰기/재생성 분리; 중복 job id/digest 감지.
- 보안: SSRF 방지(public-site라고 해도 localhost/metadata/내부 IP 접근 차단), 허가된 origin/crawl budget, DOM/XSS escape, HTML sanitization, 인가되지 않은 인증 토큰/쿠키 외부전송 금지. 기존 README/Pro 보안 gate 유지.

## 6. 50/70/85/95/100 검증 마일스톤
| 구간 | 정량 기준 예시(설계 범위) | 미충족 시 판정 |
|---|---|---|
| 0→50 | 기존 Pro 실제 FastAPI/SQLite 재검증, Fable+Astra 계약과 로컬 합성 증거→spec→앱 인수 1개 E2E | 부분/미검증 |
| 50→70 | 명시 허용된 public/local fixture 사이트 3종의 브라우저 관찰→증거→human review→새 앱 생성 E2E | URL 실관찰 부재 시 미완료 |
| 70→85 | 2+ 도메인/컴포넌트/상태·반응형, negative/security/금지 수집, source/visual difference report, 양 OS CI | synthetic-only는 한정 |
| 85→95 | 사용자 승인형 GUI/견적·납품, Windows Chrome/Edge 포함 복구·고객 제공 파일·법적 권리 리스크 사전 검증, 회귀100% 필수 | RELEASE HOLD |
| 95→100 | 사용자 승인 최종 계약·고객 인수·권리·판매/운영 정책·실서비스 보안·대응 등 전 최종 설계 합격 | **승인 없으면 미완료** |

**현재 REA_Web 원래 최종상품률: UNASSESSED(재산정 필요).** Pro의 CSV 생성/보안/CI 성공과 Fable/Astra 개별 자료는 확인되지만 **원래 URL→Fable→Astra→사람 승인→독립 앱→재검증 전체 실사이트 E2E가 확인되지 않음**. 따라서 이 제품에 기존 Lite 95%를 그대로 표기하면 안 된다. 설계 초기화/브랜치 생성은 제품 구현률 증가가 아니다.

## 7. 새 REA_Web 개발 브랜치·원본/검증
- `main`은 원래 제품 최종설계·소유권·진척 정본 (과거 기록 보존).
- `feature/website-analysis-rebuild`: **기존 Pro source `feature/d27-windows-python-discovery@97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d`**에서 안전하게 분기, Fable/Astra 상위 레이어와 기능 테스트만 추가. 원본 checkout/CI/파일에 손상 없이 단위 진척 검증.
- `feature/orchestrator@46060b4665560922d0c9cf82b9e5c08971eb9427`: 역사적 Fable bridge+Pro MVP baseline.
- `feature/evidence-adapter@fda96076de33ebf4f4b6118972a5033a3f703ba9`: Astra 검토용 제안/승인 차단 실험.
- `import/fable51-bbe72c0@7e6f273b359b207fad8f92016226e3058cbcb839`, `import/astra-p4-b3166b6@f044b66e799289a5a353fdb9cbfdb324e683ffa3`: pinned source snapshots, 변경·재배포 금지.
- 구 Lite 브랜치 `feature/lite-owner-delivery-p95-20261112`: DATA2WEB 이관 근거로 **보존**, 무단 삭제/재작업 금지.

## 8. 현재까지 관찰된 실제 근거 / 미검증
- `feature/orchestrator@46060b4`: CSV→신규 FastAPI+SQLite 앱, optional Fable1.0 JSON→Astra 검토 기록, 과거 Actions `40200704855` 합성55 PASS. **웹사이트 실관찰 E2E 아님**.
- `feature/d27-windows-python-discovery@97b6e5`: 기존 Pro 생성·Window 제약·검수 코어, 과거 GitHub 원본 기능 테스트. 아직 이 신규 분석 브랜치 기능 테스트 **NOT RUN**.
- Fable/Astra 각 원본 파일 존재·tree SHA 확인. 신규 REA_Web 사이트 분석·재구축 실통합/고객 Windows/라이선스/권리 **미검증**.
- 기존 Lite 엔지니어링95%는 독립 DATA2WEB 개발의 원출처 한정, REA_Web 본래 목표 달성률로 사용하지 않는다.
- 프로덕션/실 고객/유료 배포 없음. RELEASE HOLD.

## 9. 다음 개발 순서
1. `feature/website-analysis-rebuild`의 현 Pro API/테스트와 `feature/orchestrator`·Fable/Astra source contract를 **정확한 파일/SHA로 비교**. 무조건 전체 merge 금지.
2. 새 `site_observer`에 **허가된 로컬 HTML·브라우저 fixture**에서만 캡처·상태·결과를 먼저 구현, 외부 URL은 별도 권한 범위와 과금 확인 후.
3. observer→Fable adapter→Astra validation→human REVIEW/HOLD→Pro 생성→실 Chromium 실파일 E2E를 소량 합성으로 완료.
4. P50 다음 각 단계별 실 CI/QA를 통과하고 진척률을 **정본 요구사항** 대비 계산한다.
5. 고객 권한/운영배포·상용 권리/개인정보·가격/기대 산출물/유지보수 범위는 사용자 별도 승인 이전 활성화하지 않는다.
