# REA_Web — 증거 바인딩 기반 독립 UI 구조 생성 P95 보강 (2026-11-13 KST)

## 정체성 / 판정 기준
- 본 제품 **REA_Web**의 정본은 `REQUIREMENTS.md` / `docs/ORIGINAL_FINAL_DESIGN.md`: 허가된 참고 사이트의 Fable5.1 관찰 → Astra P4 증거·명세 → 사람 검토 → 고객이 소유한 데이터·자체 소스 기반 **독립 웹앱 구조/동작 구현** → 실제 브라우저/권리 검수.
- CSV/Excel/JSON로 HTML만 만드는 별도 `data2web_studio`나 기존 CSV 카탈로그 생성기가 원래 제품 전체가 되어서는 안 된다.
- 코드 구현 여부와 실제 고객 사용권/완료 여부는 별도로 평가한다. 합성 localhost 3개 사이트 PASS는 **공개/고객 임의 웹사이트의 자동 디자인·업무 로직 복제 성공 증거가 아니다**. 사용자 현재 P95 목표는 실사이트/고객/권리 및 인가된 UI 재구축 범위가 충족될 때 판정한다.

## 새 기능
- `rea/website_component_builder.py`:
  - `observed_contract(reference_html, fixture_sha256, p85_receipt, fable_record_summary?)`: 원본 HTML SHA와 `rea.website.p85.v1` Astra draft digest를 검증한다. desktop/mobile 각각 검색→분류→상세 세 단계, 전/후 상태와 `ObservationBundle`의 `observed` record ID·증거 ID·PNG SHA를 일대일 연결하고, 별도 P85 합성 행동 oracle와 대조해 함께 변조된 상태도 HOLD한다. **관찰된 기능/화면 후보는 실제 고객 승인 전에는 구현 권한을 갖지 않는다**.
  - 의미 구조는 `rea.website_site_layout.observe_layout_contract`의 `nav/aside/article` 등 **개수만** 사용한다. 원시 참고 HTML/CSS/JS·텍스트·이미지/브랜드·복잡한 숨겨진 로직은 출력 파일에 복사하지 않는다.
  - 선택형 원본 Fable Record 메타데이터는 `rea.website_p95.inspect_fable_record`의 제한된 localhost/mode·SHA 검사 결과만 수용한다. 생성된 오피니언의 `packet_sha256`는 실제 Astra/Record 검토 패킷의 SHA에 일치해야 한다. **Fable의 headed `--record` 실사용 조작을 현재 자동화에서 재현했다고 주장하지 않는다**.
  - `build_evidence_ui(...)`: P95 localhost GUI에서 생성·저장된 정확 `approve_synthetic_proposal` 의견, 계약 SHA, 고객 파일 기반 Pro 원본 디렉터리, 명시 `APPROVE_SYNTHETIC_LAYOUT_ONLY`를 확인. 먼저 기존 `apply_owner_layout`의 증거기반 자체 CSS 적용, 이어서 **BeautifulSoup으로 원본이 아닌 REA 자체 Pro HTML을 재배치**한다. 상단 nav links / 측면 업무영역 / article 디렉터리의 세 가지 **진짜 DOM 컴포넌트 트리**를 생성한다. `#search/#category/#count/#detail/#results/.pagination`는 원본 기능의 JS 바인딩을 보존하고 중복/누락을 차단한다.
  - 출고할 새 앱의 `review/p95_evidence_ui_contract.json`, `manifest.json.website_p95_component`에 6개 관찰상태 trace·Astra/Fable 계약 SHA·원자적 create-only 결과·UI 디자인/권리 HOLD 판정을 기록한다. 입력 HTML, 기존 생성 앱과 고객 CSV는 수정하지 않는다.
- `rea/website_ui_cli.py`: 일반 사용자용 첫 독립 UI 구조 진단/적용 명령 `inspect`, `build`; 입력은 기존 P85 로컬 증거·owner opinion·owner 소유 HTML과 고객 CSV 생성 앱. 공개 URL을 직접 접속하지 않으며 원시 Fable Record는 옵션이다.

## 실제 명령 및 단계
기존 P85 로컬 증거와 앱·원본 합성 HTML이 이미 생성된 경우에만 실행한다. 아래 값은 플레이스홀더이며 샘플 고객 동의나 실제 사용권을 뜻하지 않는다.

```bash
python -m rea.website_ui_cli inspect --reference-html source.html --fixture-sha256 FULL_SHA256 --p85-receipt previously-built/review/p85_evidence_and_visual_diff.json

# 사람의 로컬 검토 GUI에서 동일 P85 review digest + layout_preset을 고르고
# approve_synthetic_proposal 의견 JSON을 저장해야 새 앱을 생성할 수 있다.
python -m rea.website_ui_cli build --reference-html source.html --fixture-sha256 FULL_SHA256 --p85-receipt previously-built/review/p85_evidence_and_visual_diff.json --existing-app previously-built --decision opinions/REVIEW.json --approved-ui-contract-sha256 CONTRACT_SHA256 --owner-approval APPROVE_SYNTHETIC_LAYOUT_ONLY --out NEW_INDEPENDENT_APP_DIR
```

## 한계·미검증·중단 기준
- **실사용 미검증:** 실제 고객이 사용권을 승인한 public/외부 URL을 Fable headed Record로 관찰한 실증, Astra로 특정 원본 사이트의 다양한 업무 흐름/컴포넌트를 완전 명세하고 웹앱 신규 구현한 E2E, 참고 사이트의 실제 시각·반응형·디자인·저작권/라이선스 적합성 검증, 실물 Windows 10/11 사용자 인수, 개인정보/보관기간/고객 제공 파일의 법적 이용권, 결제·견적·약관, Production 배포.
- **현 기술은 제한된 로컬 합성 프로토콜 전용**이다. 원본 웹사이트의 CSS/스크립트·마크업을 복제하지 않고, 미확인 기능/폼·인증·예약 등은 자동 재현하지 않는다. 실제 고객 동의 없는 외부 사이트·인증된 URL을 자동 조사하거나 화면을 완전히 복제하지 않는다.
- REA 기존 Pro/Fable/Astra/import 브랜치·원본 자료 및 별도 DATA2WEB을 그대로 보존한다. 실패·SHA/검토 의견 불일치·기존 출력 폴더는 생성 금지/HOLD; 소스 원본 삭제/강제 덮어쓰기 금지.
- 사용자 P95 목표를 **테스트 숫자나 CSS 기반 합성 성공만으로 무단 95% 선언하지 않는다**. 정본의 85→95 전제(사용권/실고객·실사이트 재구축) 부족 시 **85% 엔지니어링 잠정 + [작업중] 유지 / RELEASE HOLD**.
- 다음 최우선은 실제 권한 있는 원본 사이트(필요 시 사용자가 허락한 로컬 자료) → Fable 실제 Record/실 DOM 관찰→Astra UI/업무 명세→소유자 승인→완전히 새로 구현한 독립 웹앱 실브라우저 비교·권리 preflight. 실 고객자료/외부 URL·권한·유료 결제·배포/판매는 사전 승인 필수.

## 검증·실패/복구
- **이 문서를 작성한 시점에는 최신 CI가 진행 중**이므로 정확 PASS/FAIL 결과는 최종 GitHub Actions 완료 후 이 문서 최상단과 `STATUS.md`/`HANDOFF.md`에 별도 반영한다.
- 기존 코드 검증 기준 P95 이전 `de335f9b65b8991c91dd3078d0044f32522f2b50`: Win2025 80PASS/0FAIL, Ubuntu24.04 78PASS/2SKIP, 2/2 SUCCESS.
- 새 구현 초기 SHA `a8a72003469deabc8da2481694353507c149779c`의 실패는 **1개 forged-state negative test**에서 subject/observation 쌍을 같이 변조해도 거부하지 못한 것. 새 원본 `rea/website_component_builder.py`에 P85 행동 oracle를 독립 비교하는 안전 검사를 추가.
- Windows 과거 SHA `3d3a771b1997870917ad5656b6ca6de40b86b738` 1FAIL은 `csv.write_text`가 `\n`을 `\r\n`으로 변환한 결과를 테스트가 잘못 비교한 것. 테스트에 **실제 입력 원본 바이트 snapshot**을 저장·재비교하여 원본 보존을 올바로 검증.
- 추가 보강: P95 reviewer `packet_sha256`를 실제 Astra(+선택적 Fable Record) packet과 일치 검증하고 `inspect`/`build` CLI를 독립 제공. 해당 변경 후 최신 CI exact SHA는 마지막 완료 run이 기준.

## KST 기록
2026-11-13 KST. 테스트는 합성 localhost·GitHub hosted Win2025/Ubuntu24.04 범위이며 판매·실외부사이트·법적권리 미검증.
