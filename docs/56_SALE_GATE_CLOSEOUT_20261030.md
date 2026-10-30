# REA_Web 출시 마감 — 검증 증거 원장 (2026-10-30)

**상태: 출시 승인 아님.** 이 문서는 기술적으로 시험된 항목과 실제 판매에 필요한 외부 판단을 분리한다. 임의로 완료율 100%를 선언하거나 서명·권리·고객 수락을 생성하지 않는다.

## 지금까지 실제로 확인된 기술 범위

- 한 건의 고객 소유 CSV / flat JSON, 명시적 필드 매핑 승인, 같은 스키마 두 파일의 승인된 ROW APPEND
- 읽기 전용 로컬 SQLite/FastAPI 목록·검색·필터·상세 및 Windows 납품 ZIP
- 합성 데이터 기반 Windows CMD/localhost/Chromium 및 Linux 자동 회귀 테스트
- 고객에게 Python 3.11 이상과 별도 설치가 필요할 수 있으며, 납품 ZIP 자체는 단독 EXE/오프라인 Python 배포물이 아님
- 검증은 임의 실제 고객 PC, 허가받은 실제 고객 데이터, 계약 검수 또는 저작권 허가를 대체하지 않음

현재 PR은 #30 (DRAFT / UNMERGED). 기존 추정 개발 95% / 판매 준비 77%는 재산정하지 않았으며 판매 승인을 뜻하지 않는다.

## 출시 판정 원장 도구

프로젝트 루트에서 Python 3.11+로 실행한다. 이 스크립트는 **Python 표준 라이브러리만 사용**하고 고객 데이터에 접근하거나 서버·네트워크를 실행하지 않는다.

```powershell
$sha = (git rev-parse HEAD).Trim()
python scripts/rea_sale_gate.py --init .\local_sale_gate_evidence.json --source-sha $sha
python scripts/rea_sale_gate.py --check .\local_sale_gate_evidence.json --source-sha $sha
```

Git 메타데이터가 없는 ZIP 스냅샷 작업자는 GitHub의 정확한 40자리 브랜치 커밋 SHA를 직접 확인해 `--source-sha`에 사용한다. **이 템플릿은 기본적으로 전 항목 NOT_RUN이며 평가 시 종료 코드 2, BLOCKED다.** 동일 파일 초기화는 덮어쓰기 없이 실패한다. 개인 정보·실제 고객 파일·비밀번호는 원장에 넣지 않는다. 원장은 저장소에 커밋하지 말고 별도 비공개 위치에 보관한다.

원장에 있는 각 항목을 실제로 검토한 사람이 `VERIFIED`로 바꾸고 `reviewer`, `verified_on`(YYYY-MM-DD), `evidence_refs`(안전한 증거 위치/문서 ID)를 기록한다. 스크립트는 필수 6개 항목 중 하나라도 비어 있거나 대상 소스 SHA가 바뀌면 BLOCKED다. **전 항목 기입 후에도 출력은 READY_FOR_SELLER_FINAL_REVIEW이며, 절대 자동 판매 승인이 아니다.** 기재한 증거의 진위·법률적 유효성은 프로그램이 독립적으로 검증하지 않는다.

## 사람에게 남은 여섯 조건

| 게이트 | 외부 검증의 최소 근거 | 관련 문서 |
| --- | --- | --- |
| independent_windows_operator | 개발에 참여하지 않은 일반 Windows 사용자가 합성 데이터 ZIP 설치·실행·검색·백업·복구를 직접 수행하고 실제 결과/날짜 기록 | docs/52_WINDOWS_CUSTOMER_ACCEPTANCE_PROTOCOL_NOT_RUN.md |
| source_redistribution_rights | 납품 ZIP에 포함된 REA 원본·생성 코드의 사용/수정/상업적 재배포 권리와 권리자의 확인 기록 | docs/25_SOURCE_LICENSE_AUDIT.md |
| dependency_license_notices | 실제 납품되는 파일/의존성의 정확한 범위, 버전·라이선스·고지 의무 확인. 개발 PC 메타데이터 관찰은 증거 일부일 뿐 | docs/48_RUNTIME_DISTRIBUTION_REVIEW.md |
| privacy_data_operations | 권리 있는 비민감 자료만 받는 절차, ZIP에 평문 SQLite 포함 고지, 전달·보존·접근·삭제 운영 및 고객 동의 | docs/53_DATA_HANDLING_REVIEW_NOT_APPROVED.md |
| seller_scope_terms | 기능·가격·납기·지원·수정·취소/환불 범위, 플랫폼 정책 확인 및 판매자 승인 | docs/07_KMONG_OFFER.md, docs/51_KMONG_SALE_GATE_20261030.md |
| measured_delivery_rehearsal | 일반 사용자의 실제 견적→생성→검수→ZIP 전달 작업 시간 기록. 합성 CI 시간으로 대체 금지 | docs/30_THREE_CASE_QUOTE_REHEARSAL.md |

**예시의 `VERIFIED` 데이터를 복사해 판매 승인의 증거로 사용하지 않는다.** 특히 Fable/Astra는 현재 판매 범위에서 제외되어 있지만, 코드와 고객 ZIP에 무엇이 포함되는지 실물 기준으로 확인해야 한다.

## 진입/출시 결정

1. 판매용 범위는 **고객 소유 비민감 CSV/flat JSON → 명시적 승인 → 로컬 읽기 전용 웹앱**으로 제한한다. 크롤링, 호스팅, 결제, 로그인, 타 스키마 JOIN, 무제한 유지보수는 미포함.
2. 여섯 검수에 진짜 근거가 준비되면 원장을 작성하고 정확한 최종 커밋 SHA로 재검증한다.
3. 이후 판매자/권리자/필요한 전문 검토자가 별도 출시 여부를 승인한다. 코드의 `NOT_COMMERCIALLY_APPROVED` 배너를 미리 제거하거나 고객 자료를 무단 사용하지 않는다.
4. 승인 전에는 크몽 주문 접수·판매 가능·100% 완료로 표시하지 않는다.

기계적 게이트 코드와 회귀 테스트: `scripts/rea_sale_gate.py`, `tests/test_sale_gate.py`. 도구 단독 시험 6 PASS는 해당 검사기의 기능만 검증한다.
