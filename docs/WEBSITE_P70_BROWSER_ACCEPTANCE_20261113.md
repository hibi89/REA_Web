# REA_Web 원래 웹사이트 분석·재구축 P70 — 로컬 3사이트 Chromium/Astra/Pro 검증 (2026-11-13 KST)

## 검증 정본 / 완료 판단
- 제품: `hibi89/REA_Web`, 분기 `feature/website-analysis-rebuild`, 원래 목적: 권한 있는 사이트 관찰→Fable5.1/Astra P4 증거화→인간 검토→고객 소유 자료로 독립 웹서비스 생성·실동작 확인.
- **검증된 정확한 코드+CI SHA: `bfac1116ac7a20c7162f42a59e51277d402b24d9`.**
- **[GitHub Actions Run #43266467950](https://github.com/hibi89/REA_Web/actions/runs/43266467950) = SUCCESS, 2/2 jobs**.
  - Ubuntu 24.04 Python 3.11/실 Chromium: **41 PASS / 0 FAIL / 경고1**.
  - Windows Server 2025 Python 3.11/실 Chromium: **41 PASS / 0 FAIL / 경고1**.
  - 명령: `python -m pytest -q tests/test_website_rebuild_p50.py tests/test_website_p70.py tests/test_orchestrator.py`; 실제 frozen Fable `7e6f273b359b207fad8f92016226e3058cbcb839`와 Astra `f044b66e799289a5a353fdb9cbfdb324e683ffa3` 고정 checkout.
- 신규 변경 소스: `rea/website_p70.py` / `tests/test_website_p70.py` / `.github/workflows/rea-website-p50.yml`. 기존 P50 `rea/website_rebuild.py`, Pro 원본/대화형 REA Lite 코드 변경 없음.
- **현 단계 판정: 70% 엔지니어링 잠정 (정본 최종설계의 50→70 로컬 3사이트 브라우저 합성 수용관문을 충족); 실제 외부 사이트/임의 고객 사이트 재구축·판매는 완료 아님. RELEASE HOLD, Production/배포 미적용.**

## 3가지 허가된 합성 사이트 실제 검증 범위
| 독립 로컬 HTML 샘플 | 실제 Chromium 제어 | 관찰 근거 | 생성 REA Pro 앱 검증 |
|---|---|---|---|
| catalog | 검색어 `커피` 입력 | `#count`: `3건`→`1건`; 실제 전·후 Chromium PNG SHA/evidence | 기존 독립 웹앱의 실제 검색 UI `3건`→`1건` |
| inventory | 분류 `음료` 선택 | `#count`: `3건`→`2건`; 실제 전·후 Chromium PNG SHA/evidence | 생성된 앱에서 카테고리 선택 `3건`→`2건` |
| directory | 상세 버튼 클릭 | `#detail`: 빈 값→`커피`; 실제 전·후 Chromium PNG SHA/evidence | 생성된 앱의 항목 클릭 `#detail h3`에 `커피` |

- 각 사이트는 합성 HTML+JS이며, 서로 다른 3개 페이지 레이아웃을 실제 `127.0.0.1` HTTP 서버에 띄워 **실 Chromium DOM 상호작용**을 테스트했다. 이것은 브라우저 `page.set_content`만의 mock이 아니라 실제 로컬 HTTP 페이지 로딩/이벤트다.
- 사전 입력 파일 SHA와 user-supplied fixture SHA를 검증. 기존 P50 `rebuild_local_fixture` 호출이 **고정 Fable 5.1 실제 정적 스캐너**의 loopback 단일 GET과 **Astra P4 실제 계약** 검사 수행. P70 신규 브라우저 행동 캡처는 **별도 Playwright 관찰기**이며, 원본 Fable 5.1의 `--record` 모드를 실행했다고 주장하지 않는다.
- `ObservationBundle`에 `certainty=observed`, 스크린샷 전·후 증거 링크 및 UI state before/after, `derive_spec`를 실행하여 1개 observed candidate feature를 생성. **Astra `candidate_features[].review_status=requires_review`, `approval_gates[].status=pending`, `implementation_ready=false` 유지**.
- 관찰기는 대역 제한 브라우저 컨텍스트/HTTP CSP로 외부 URL/네트워크 및 service workers를 차단한다. 원시 참고 HTML·JS·타사이트 콘텐츠를 새 앱으로 복제하지 않으며, 기존 Pro 생성기는 소유자 승인된 **별도 합성 CSV 3행**만 입력한다. 3건부터 시작하는 기능 동작의 **좁은 결과 동등성**만 검수했으며 고객 사이트의 전체 설계·픽셀·동적 동작 복제 여부는 미검증.
- 검토 영수증은 `inspect`로 관찰 결과 digest를 출력한다. `build`는 명시된 `APPROVE_SYNTHETIC_ONLY` + 소유자 CSV 및 fixture SHA + 정확 이전 review digest 재제시 후 새 생성 대상에만 배포한다. 문서·테스트에서 사용한 승인 토큰은 **자동화된 합성 검증 승인 시뮬레이션**으로서 실제 고객·제3자 사이트 관찰/사용 허가의 증거가 아니다.
- 결과물에 서버로 노출되지 않는 `review/p70_browser_evidence.json`, `review/p70_before.png`, `review/p70_after.png`와 app manifest가 포함되고, 생성 앱 `/review` 경로는 404로 차단된다(기존 P50 회귀).
- 승인 digest 위조/불일치·원본 파일 SHA 변경·누락된 승낙·충돌하는 출력 경로·모르는 UI 행동은 **새 산출 디렉토리 생성 전/게시 전 거부**, 기존 소유자 파일 보존. 기존 P50 테스트 31개와 신규 P70 테스트 10개를 단일 SHA에서 통합 검증.

## 남은 범위·상용 판정
- **미구현/미검증:** 실제 임의 웹사이트의 브라우저 방문·UI 구조/복잡한 동적 상태/반응형·스타일을 기능 단위로 재구축, 실제 고객 소유/사용권 명시 문서와 인수, public URL 스캔 허가·ToS/robots 검토, 실제 Win10/11 구매자 환경, 웹앱 프로덕션 배포, 라이선스/NOTICE·가격·지원/환불/판매 GO.
- Fable 5.1 실제 `--record`의 사용자 조작 기록과 P70 별도 Playwright 관찰기 통합, **실제 인간 검토 UI로 증거를 승인한 뒤 해당 동작을 생성기 설계에 반영**하는 과정은 다음 단계다.
- 현재 생성 독립 웹앱은 기본 read-only 카탈로그/검색·필터·상세를 구현하며 사이트의 스타일·상표/자산·복잡한 업무 기능을 자동 재구축하지 않는다. 단계 70%는 제품 전체 능력의 객관적 70% 측정치가 아닌 **사용자가 승인한 단계적 설계 수용 기준의 내부 잠정 평가**다.
- 다음 P85 후보: 2개 이상의 상호작용 상태/복잡 사이트·접근성·반응형/visual diff, Fable Record 실제 소스, 독립 구현 요소별 signed owner approval/권리, Windows/Ubuntu 다중 브라우저 증거 및 실패 복구.

## 원본/복구/보안/인수인계
- 원본 Pro `feature/d27-windows-python-discovery@97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d`, Fable Import `import/fable51-bbe72c0` pinned SHA `7e6f273b...`, Astra Import `import/astra-p4-b3166b6` pinned SHA `f044b66e...`, Data2web Studio Private 별도 repo. **원본 코드는 수정하거나 강제 merge하지 않음.**
- GitHub에는 코드·문서·합성 fixture/test만; 고객 원본 데이터/토큰은 저장/전송하지 않았으며 API/LLM 호출 및 실도메인 배포 없음.
- P50 검증 SHA `fb67616df6a5e7eb7ea14c1315a58dd689d2534d`는 보존; P70 기능 검증·복구 기준 `bfac1116ac7a20c7162f42a59e51277d402b24d9`.
- 2026-11-13 KST. 검증 근거는 정확 해당 GitHub Actions 완료 시점 기준. 후속 문서 커밋은 **실행 검증 SHA와 별개**로 추적한다.
