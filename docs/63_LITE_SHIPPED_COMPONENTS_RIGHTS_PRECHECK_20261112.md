# REA_Web Lite 납품물 구성·사용권 사전검토 — 2026-11-12 KST

## 결론: 납품물 구성 확인 / 법적 출고 승인 NOT_GRANTED

- 범위: 비공개 저장소 `hibi89/REA_Web`의 `feature/lite-owner-delivery-p95-20261112` 브랜치 정적 소스 조사. 이번 검토 HEAD 기준 코드는 이전 기능 CI와 동일하며, 마지막 기능 검증 SHA는 `cb7df1f4d1ce517c5940570af5bb1085410de268` ([Actions #43186105405](https://github.com/hibi89/REA_Web/actions/runs/43186105405), Windows+Ubuntu 2/2 SUCCESS).
- 이번에 확인한 파일: `rea/lite_builder.py`, `rea/lite_assets/template.html`, `rea/lite_delivery.py`, `rea/lite_owner_kit.py`, `rea/mvp.py`, `docs/25_SOURCE_LICENSE_AUDIT.md`, `docs/59_RUNTIME_LICENSE_CROSS_OS_EVIDENCE_20261031.md`, `docs/62_LITE_FINAL_SELLER_ACCEPTANCE_20261112.md`.
- **정적 코드·기존 CI 근거**이며, 소유자 서명·법률 검토·실제 고객 데이터 권한·새로운 실행 테스트가 아니다. 기술 완성률 95% 잠정 유지, 판매 `RELEASE HOLD`.

## 1. 실제 Lite 고객 ZIP의 고정 구성

`rea/lite_delivery.py`의 `FILES`는 정확히 다음 3개이고, `verify_lite_zip`은 추가/중복 ZIP 멤버를 거부한다.

| ZIP 멤버 | 실제 용도 | 데이터·권리 위험 |
|---|---|---|
| `catalog.html` | 고객 CSV/JSON에서 생성된 단일 HTML. 내장 CSS, JS, JSON 데이터, 목록·검색·필터·편집 CSV→새 HTML 내보내기 | **고객 행 데이터가 평문 포함됨.** 내장 HTML/CSS/JS 템플릿의 복제·재배포 권한 확인 필요 |
| `manifest.json` | HTML SHA256/바이트 수, 행·열 수, `sale_approved=false` 등 무결성 메타데이터 | 서명·작성자 신원·사용권 증빙 불가. 메타데이터도 공유 전 확인 필요 |
| `README_KO.txt` | 오프라인 실행 및 평문/판매 HOLD 고지 | 내용은 안내, 승인 증거 아님 |

위 **Lite ZIP 코드 경로에는** Pro 런타임용 `fastapi`, `uvicorn`, Python 실행기, wheel, `.env`, Fable/Astra 소스 파일, 독립 DB/SQLite 설치파일을 넣는 분기나 선언이 없다. 추가 멤버가 있으면 검증에서 실패해야 한다. 판매자 작업공간의 Python 소스나 실제 입력 CSV는 구매자 ZIP에 직접 복사하도록 설계되지 않았다. 단, **사용자 데이터 값은 HTML 안에 복사됨**. 이는 Pro 고객 ZIP의 라이선스 실태를 대체하지 않는다.

## 2. 빌드 환경과 고객 실행 환경을 구분

- **판매자/생성기:** `rea.lite_owner_kit` → `rea.lite_builder` → `rea.mvp`의 로컬 CSV/JSON 파서를 호출. Python 환경과 원본 저장소가 있어야 생성 가능하며, 패키지 제작·검증은 표준 라이브러리 기반.
- **고객/Lite HTML:** Python, pip, 별도 웹 서버 및 네트워크 접속을 요구하지 않음. 템플릿은 HTML 안의 자체 CSS/JS를 사용하며 시스템 글꼴을 참조한다. 정적 검색에서 외부 스크립트/CDN/웹폰트 요청 선언을 확인하지 못했고 CSP에 `connect-src 'none'`이 설정되어 있다. 이것은 **모든 OS/브라우저·고객 정책에서 오프라인 실행이 반드시 가능함을 증명하지는 않음**.
- **Pro 제품:** 서버용 앱, requirements, SQLite가 달라 배포 자산·런타임 의무가 다르다. 2026-10-26 `docs/25_SOURCE_LICENSE_AUDIT.md`와 2026-10-31 `docs/59_RUNTIME_LICENSE_CROSS_OS_EVIDENCE_20261031.md`의 14패키지 Windows/Linux 라이선스 메타데이터 검증은 **Pro/runtime에 대한 과거 부분 증거**다. 이를 Lite 고객 ZIP에 설치되는 14개 패키지라고 잘못 설명하면 안 된다.

## 3. 법률/프라이버시 미해결 사항 — 사람의 판단 필요

| 심사항목 | 현재 확인된 사실 | 남은 판정 |
|---|---|---|
| Lite HTML/CSS/JS 원천 | 리포지토리 내 템플릿·빌더와 생성기 흐름 확인 | 실제 저작권자·기여자·고객 재배포 허락 범위 **미확인** |
| 루트 LICENSE/NOTICE | 현재 브랜치 파일 트리에서 표준 루트 `LICENSE`·`NOTICE`를 발견하지 못함 | 부재는 권리의 부존재나 판매 허가를 의미하지 않음. 배포 계약/필요 고지 문안 **미승인** |
| Fable/Astra 제3자 원천 | 기존 Pro 원천 감사 문서에 고정된 소스 사본 및 권리 UNKNOWN 기록 | Lite ZIP에 직접 동봉되지 않는 것과 판매자 측 사용·개별 기여자의 권리 해결은 별개 |
| 고객 데이터 | Lite `catalog.html`에 원본 행이 평문 포함. ZIP에 별도 원본 CSV는 들어가지 않음 | 데이터 소유·동의·공유대상·보관/삭제·유출 위험 판단 **미승인** |
| 고객 Windows·업종 인수 | 호스팅 CI 합성 3업종 파일 저장/재열기 PASS | 실제 비개발자 Windows10/11 및 사람 3건 acceptance **NOT_RUN** |
| 크몽 조건 | 기존 `docs/07_KMONG_OFFER.md`는 가격·지원·환불 초안으로 명시 | 제품별 판매가격·범위·제공자료·지원/환불·상용 승인 **미승인** |

## 4. 권고하는 최단 경로

1. **사전 조사까지는 완료:** Lite 실제 ZIP 3개 구성과 과거 Pro 의존성 감사의 범위를 분리했다. 새로운 개발/반복 CI를 요구하지 않는다.
2. **권리자가 판단할 사항:** 템플릿 원천·기여·고객 사용권 및 필요한 NOTICE 확인, 승인된 비민감 3종 예시 데이터와 전달 조건 결정.
3. **고객 인수:** 비개발자 Windows10/11의 브라우저 파일 더블클릭/교체/다운로드/재열기, 카페·재고·사무 각각 1회 인간 측정·인수기록 확보.
4. **출고 판단:** `docs/62_LITE_FINAL_SELLER_ACCEPTANCE_20261112.md`와 기존 `scripts/rea_sale_gate.py`의 증빙 게이트에서 실제 검수자가 승인하기 전에는 Draft PR 미병합, 고객 파일 전송·크몽 공개 판매 금지.

**안전성:** 원본 Pro/Lite/고객 데이터/원본 브랜치 미수정. 현재 Draft PR #34는 미병합 상태로 유지. Vercel/Production 미적용. 새 코드/CI 테스트 수행 없음; 이 검토를 96~100% 진척으로 계산하지 않는다.
