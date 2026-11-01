# REA_WEB Lite — Pro source integration (2026-11-01)

## Boundaries and source

- Work branch `feature/rea-lite-integrated-20261101`, derived from the existing Pro branch head `97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d`. Do not overwrite Pro or merge to main without release review.
- Original archived Lite candidate SHA256: `8078e56cceedb17f5cbaa40eb032c502fb309d0c475be2f7bfc48c06afb5edc8`. Original template reconstructed exactly from synthetic archived cafe HTML; Git blob `70387cfaf58af6c4fc633ab96e465c819bdec440`, identical to locally archived template. No purchased/customer data in repository.
- Uses Pro's original `parse_input`, `map_owner_fields`, `source_sha256` directly. Seller needs Python 3.11+ and checkout; **customer needs only HTML browser and no server or Python**.
- CSV or flat JSON input allowed to seller. Customer browser updates only by same-header UTF-8 CSV with mandatory unique ID/title/category. 10 MiB max, 10,000 rows, 20 fields, 2,000 chars per cell. No source overwrite, approvals required before generation.
- Three theme variants `cafe`, `inventory`, `office`; list/search/sort/category/details/pagination, local CSV update and new-HTML export. Records embedded as plaintext: do not use sensitive/private data until explicit processing policy. Do not upload HTML to websites.

## Synthetic owner workflow

Run from checked-out repo root:

```shell
python -m rea.lite_builder inspect --source samples/rea_lite_inventory_synthetic.csv
```

Inspect the SHA256 and schema. Choose a NEW output path (must not exist), and substitute the reported SHA below:

```shell
python -m rea.lite_builder build --source samples/rea_lite_inventory_synthetic.csv --out demo_inventory_NEW.html --id-field item_code --title-field item_name --category-field group --source-sha256 <INSPECTED_SHA256> --confirm APPROVE --theme inventory --name "Synthetic inventory"
```

Open the generated `demo_inventory_NEW.html` with Edge/Chrome. Change CSV only with exact original header names, then **download the new HTML**, close the old page, open the saved file, and confirm the updated item persists. A failed CSV must retain previous records. Files are not silently overwritten; avoid including secrets in either input or generated output.

## Evidence and test commands

```shell
python -m pytest -q tests/test_rea_lite_integration.py
node tests/test_rea_lite_csv.cjs
python -m pytest -q tests/test_rea_lite_browser.py
```

Browser tests require Playwright's Chromium. GitHub Actions `.github/workflows/rea-lite.yml` runs these against actual Pro code with Python3.11/Node22 on Windows and Linux. [Automated job #41302599725](https://github.com/hibi89/REA_Web/actions/runs/41302599725) was successful on `f0e088e`: real generated file:// navigation, unsafe CSV denial, CSV update, Blob download, file:// reopened data and no external network request. This is **not human Windows acceptance**.

## Release gates (all required)

- Windows 10/11 actual user Edge/Chrome double-click and review, file:// CSV upload + exported HTML persistence, Console/Network check and support UX.
- Owner's exact original source rights, vendor and wheel LICENSE/NOTICE obligations, no misleading IP claims.
- Approved customer privacy/data retention policy for plaintext embedded HTML, terms, refund/support boundaries, pricing and 3 measured end-to-end delivery rehearsals.
- Explicit owner GO before any seller listing, public ZIP, user data, merge to release branch or distribution.

Current status: **TECHNICAL INTEGRATION VERIFIED / COMMERCIAL RELEASE HOLD**. Pro original scope and known tested behavior preserved; hosted production N/A.


## 2026-11-01 — 미저장 변경 경고 보강 / 검수 ZIP 갱신

- 검증된 기능 SHA: `5ec1d6c290ab2322029d641f2535221883eaa1e5`, [실제 Actions Windows/Linux 2/2 성공](https://github.com/hibi89/REA_Web/actions/runs/41306179899).
- CSV 정상 반영 이후, 새 HTML을 저장하지 않고 창을 닫거나 새로고침하면 `beforeunload`을 통해 **브라우저에 경고를 요청**합니다. 이 팝업은 브라우저 정책과 사용자 클릭 이력에 따라 나타나지 않을 수 있으므로 저장을 보장하지 않습니다. 실패한 CSV 갱신은 경고를 활성화하지 않습니다. 다운로드를 요청해도 실제 파일 저장 확인 전 경고는 유지됩니다.
- 로컬/세션 스토리지 자동저장은 의도적으로 없습니다. HTML 자체에 레코드가 평문 포함되므로 외부 공유 및 고객 민감정보 사용 금지.
- Windows와 Linux 각 환경: Pro 원본 파서 7 PASS, Node CSV/escape 15/15 PASS, 진짜 `file://` Chromium 5 PASS, 패키징 3 PASS. 신규 ZIP `ca9f4f63712a51acf56e261d3c3ad1cb2ad9290866d09bd5c8416c21abfe3a5a` (23,148 B) 무결성 검증.
- 기존 archive template은 Git blob `70387cfa`; 현재 파일은 이탈 경고가 추가된 **파생 버전** `5ee764ab03a5e4ea818abb3b9cc589214d3cbdbe`입니다. 예전 "복원한 원본 템플릿 바이트 동일"은 당시 기준 사실이며 현재 코드의 동일성 주장에 사용하지 마세요.
- 현재 최신 키트는 작업 대화 파일 `REA_WEB_Lite_UnsavedGuard_Windows_Pilot_20261101.zip` (세션 임시, 향후 재현은 GitHub에서)입니다. 배포·판매가 아니라 합성 샘플 사용자 수용용입니다. 사람의 Windows Edge 수동 검수·세 번 납품 실측·실제 배포 라이선스/NOTICE·고객 정책/판매 승인은 여전히 필요합니다.
