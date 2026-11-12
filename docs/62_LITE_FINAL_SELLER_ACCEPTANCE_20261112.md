> **2026-11-12 KST scope clarification:** [actual Lite ZIP contents and redistribution precheck](63_LITE_SHIPPED_COMPONENTS_RIGHTS_PRECHECK_20261112.md) records ZIP exactly 3 members; Pro runtime wheel inventory is not a Lite customer bundle inventory. No automatic sale clearance; rights/privacy/human acceptance still HOLD.

# REA_Web Lite — 95% 기술완성 마감 / 실제 판매 전 인수 체크리스트

**기준:** 2026-11-12 KST · REA_Web `feature/lite-owner-delivery-p95-20261112` · 확인한 기능·CI SHA `cb7df1f4d1ce517c5940570af5bb1085410de268`

**판정:** **기술 95% 잠정 / 고객 인수 미검증 / 상용 판매 미승인 / RELEASE HOLD**. 본 문서와 GitHub Draft PR은 판매허가·개인정보 동의·저작권 보유의 증빙이 아니다.

## 1. 실제로 검증된 기술 범위

- SHA로 확정한 소유자 승인 CSV 또는 단순 JSON → 서버 없는 오프라인 단일 HTML.
- 판매자용 단일 실행: HTML + 무결성 영수증을 포함한 납품 ZIP을 기존 파일 덮어쓰기 없이 생성. 정상 완료 후에도 원본 불변.
- 목록/검색/카테고리/상세, 사용자 CSV 변경 → HTML 저장 → 재열기. 잘못된 CSV와 HTML 삽입문은 원본 데이터 보존 또는 무해한 텍스트로 처리.
- [Actions #43186105405](https://github.com/hibi89/REA_Web/actions/runs/43186105405): **Windows2025 전체 688 PASS/19 SKIP/0 FAIL; Ubuntu24.04 전체 677 PASS/20 SKIP/0 FAIL; CI 2/2 SUCCESS**. 카페·재고·사무 합성 3종에서 **실제 브라우저 다운로드 파일을 디스크에 저장한 뒤 ZIP 무결성 검사·file:// 재열기 PASS**. GitHub 호스팅 환경에서만 수행했으므로 사용자의 Windows10/11·실고객 acceptance가 아님.
- 고객측 HTML은 **Python/서버를 요구하지 않음**. 판매자측 생성은 Python 및 로컬 저장소가 필요함. 실제 브라우저 파일 저장·열기는 사용자 보안 정책에 따라 다를 수 있음.

## 2. 소유자/판매자 로컬 실행 절차 (실제 승인 자료만)

1. **권리 검토:** 제공받은 파일의 소유자·사용 목적·배포 대상·보관/삭제 정책 확인. 개인정보/민감정보/영업기밀은 무단 사용하지 않음. 이 HTML은 **내용이 평문으로 들어가므로** 암호화/접근제어 상품이 아님.
2. **검사:** `python -m rea.guided inspect --csv "C:\Private\approved.csv"` (JSON이면 `--json`)로 컬럼명·행 수·64자리 SHA256만 검토. 실제 값은 표시하지 않으나 열 이름도 기밀일 수 있으므로 공유하지 않음.
3. **필드 매핑:** 고유하고 기존에 존재하는 ID/제목/분류 열을 담당자가 직접 지정. 자동 의미 추론이나 변환 승인 금지.
4. **빈 새 출력 폴더 생성 후 단일 명령 실행:**

```powershell
python -m rea.lite_owner_kit `
  --source "C:\Private\approved.csv" `
  --out-dir "C:\Private\new-empty-output" `
  --source-sha256 "검사에서확인한정확한64자리sha256" `
  --id-field "식별자" --title-field "이름" --category-field "분류" `
  --confirm APPROVE --acknowledge-plaintext ACK_PLAINTEXT_LOCAL_DATA `
  --theme cafe --name "고객 승인 카탈로그"
```

5. **독립 검증:** `python -m rea.lite_delivery verify --zip "C:\Private\new-empty-output\REA_Lite_Delivery.zip"`. 결과가 `UNSIGNED_LOCAL_PACKAGE_VERIFIED_RELEASE_HOLD`라도 **서명·진본·판매 승인이 아닌 바이트 무결성 검사**일 뿐.
6. **납품 전 최종 승인:** `REA_Lite.html` 직접 열기·CSV 교체·새 HTML 저장 후 재열기, 원본 보존·재실행 확인. 사용자에게 평문 노출과 오프라인 한계 설명. 허용권리/약관 검수 전에는 **고객에게 파일을 배포하지 않음**.

CLI 영수증과 ZIP 매니페스트에는 셀 내용이 아니라 해시/행·열 숫자 및 상태가 포함됨. **HTML 본문에는 승인된 원본 행의 실제 값이 평문 포함**됨. ZIP 내부 README와 계약서/권리 검토를 분리해 보관.

## 3. 실제 고객 인수 체크리스트 — 현재 모두 NOT_RUN

| 게이트 | 사람이 확인할 실증 | 현재 상태 |
|---|---|---|
| Windows 사용자 | **비개발자** Windows10/11 Chrome/Edge에서 ZIP 추출, HTML 더블클릭/검색/필터/상세/CSV 새 저장·다운로드·재열기 (브라우저/OS 버전 및 장애 기록) | NOT_RUN |
| 3개 업종 운영자 | 카페·재고·사무 각각 비민감 승인 자료 또는 별도 허용된 시험 자료로 실제 납품 시간, 수정·복구, 오류 1회 이상 측정 | NOT_RUN |
| 원본·재배포 권리 | 판매자 원본 권리, 3rd-party 소스·런타임·NOTICE 확인, 고객 데이터 사용·재배포 동의 | NOT_APPROVED |
| 개인정보·보안 | 데이터 평문 전달 허용 여부, 전송/보관/삭제 기간, 백업·접근권한·유출 사고 대응 | NOT_APPROVED |
| 판매 조건 | Lite/Pro 판매범위 구분, 가격, 납기, 수정·지원·환불·취소 등 크몽 약관 검토 | NOT_APPROVED |
| 최종 출고 | 위 자료의 인간 검토·서명 또는 명시적 승인 및 파일 최종 SHA 일치 | NOT_APPROVED |

**저장소 점검 사실:** 이 기능 브랜치 루트에서 `LICENSE` 파일은 조회되지 않았음. 이는 저작권의 부존재를 뜻하지 않으며, **재배포 권리와 NOTICE 검토가 끝났다는 뜻도 아님**. 기존 원본/외부 컴포넌트의 사용권은 권리자가 검증해야 함.

## 4. 승인 증거 관리 (가짜 PASS 금지)

기존 REA_Web 판매 차단기 `scripts/rea_sale_gate.py`에는 사람 검수 6게이트가 이미 구현되어 있다. 이 도구는 JSON 기록의 누락만 검사하며 적법성을 자동 증명하지 않는다.

```powershell
# 새 원본 SHA에 묶인 비공개 검토 장부 생성 (기존 파일 덮어쓰기 금지)
python -m scripts.rea_sale_gate --init "C:\Private\rea-owner-acceptance.json" --source-sha cb7df1f4d1ce517c5940570af5bb1085410de268

# 사람 검토 전에는 차단 결과가 정상이므로 "실패=버그"로 해석하지 않는다.
python -m scripts.rea_sale_gate --check "C:\Private\rea-owner-acceptance.json" --source-sha cb7df1f4d1ce517c5940570af5bb1085410de268
```

검수 장부는 본인 로컬 비공개 저장소에만 보관하고, 파일 원문·개인정보·계정·토큰을 GitHub 이슈/PR에 붙이지 않는다. 검수 대상 코드가 바뀌면 다시 해당 **정확한 소스 SHA**를 기준으로 검사해야 한다.

## 5. 브랜치 운영과 완료 정의

- 원본 Lite: `feature/lite-offline-html-20261112` @ `f842d288037f9d5e4234cba170f188329b68b776` 유지.
- 이번 확장: `feature/lite-owner-delivery-p95-20261112`; 기능검증 SHA `cb7df1f4d1ce517c5940570af5bb1085410de268` (이후 **문서 커밋은 별도**).
- PR은 병합하지 않는 **Draft**로 유지. 원본 Pro/main과 고객 데이터에는 커밋/배포하지 않는다.
- Vercel·공개 Production **미적용**. CI 성공은 고객 환경 검수 및 상업적 출고가 아님.
- 롤백: 위 원본 Lite SHA에서 재개하거나 전용 확장 브랜치를 미병합으로 유지. 강제 push/기록 변경 금지.
- **95%는 최종 기술 설계 기준 정성 엔지니어링 수준**이며, 판매준비 및 사업의 100% 완료 판정이 아님.

**다음 행동:** 형의 개입이 필요한 6개 인수 게이트를 1회에 묶어 승인·검증한 후에만 크몽 판매 출고를 별도로 판단한다. 현 단계에서는 임의 상품 등록, 고객 파일 전송, 공개 배포, 실제 거래를 하지 않는다.

**확인 시점:** 2026-11-12 KST · 정확 기능 CI #43186105405. 최신 상태는 `HANDOFF.md` → `STATUS.md` → `AGENTS.md` → 본 문서 → 코드 순서로 확인.
