# REA_Web — 웹서비스 분석·재구축 자동화 엔진

> PROJECT BOOTSTRAP · 2026-10-25 · **통합 제품 미완성** · 통합 테스트 미실행

**목적:** Fable 5.1의 정적/브라우저 관찰 및 API 계약 후보를 입력으로 받아, Astra Web Catcher의 근거 기반 기능 명세·데이터 매핑·독립 웹앱 개발 기능과 연결한다. 최종 목표는 **고객이 제공하는 CSV/JSON 중심의 데이터로 작동하는 별도 웹앱**을 생성하고 검증하는 것이다.

### 현재 상태
- REA_Web 저장소 구조·설계·개발 체크포인트: 23 bootstrap files on main, updated status/handoff and vendor checker
- Fable 5.1 원본: hibi89/fable5.1_web_catcher, baseline bbe72c0acd3a3e355062d6bd0d866af33e5274b0
- Astra 원본: hibi89/astra_web_catcher, baseline main dc23ee604d02513c890615a3a98440c1ea8a5270; p4 working codex-p4-20261019 274402a3d8eaf33d9ff55bf740208a1dbded3bef
- **주의:** 원본 두 제품의 개별 테스트는 REA_Web 통합 E2E 성공을 뜻하지 않는다.

### 원칙
1. 원본 저장소는 변경하지 않는다. 버전 고정 소스는 별도 import 브랜치에만 보존한다.
2. Fable은 **관찰·추정 엔진**, Astra는 **기능 명세·개발 엔진**이다. 미관찰 서버 로직·DB·API를 발견한 것으로 가장하지 않는다.
3. **개인용 CSV/JSON + 샘플 DB 먼저** 검증. 고객 운영 DB 접속, 데이터 수집 대행, 결제 및 복잡한 인증은 기본 범위에서 제외한다.
4. 실제 사이트 분석에는 소유·분석 권한이 필요하다. 로그인/접근통제 우회 및 비공개 소스 추출을 하지 않는다.
5. 데이터의 출처, 추측, 사람의 승인, 테스트 결과를 구분한다. 기능을 완성했다고 주장하려면 실제 실행·E2E 로그가 있어야 한다.
6. 30만원 상품은 범위가 작은 **정액 납품 패키지**이며, 무제한 개발 계약이 아니다.

### 시작 안내
- 총괄/개발 담당자: AGENTS.md → docs/08_BRANCH_POLICY.md → docs/13_WORK_BREAKDOWN.md → docs/17_NEXT_TASK.md
- 제품/설계: docs/01_PRODUCT_SCOPE.md · docs/02_ARCHITECTURE.md · docs/09_DATA_CONTRACT.md
- 일정·품질: docs/04_ROADMAP.md · docs/05_ACCEPTANCE.md · docs/10_TEST_MATRIX.md
- 사업·안전: docs/07_KMONG_OFFER.md · docs/06_SAFETY_AND_LEGAL.md
- 인수인계: STATUS.md · HANDOFF.md

**첫 유료 판매 전 게이트:** 샘플 3종 동작 + Windows 실제 실행 + 기능/원문 보존 검수 + 작업시간 실측 + 계약 범위 확정.

## 새 채팅에서 복원
**[REA_Web 총괄 깃헙 레포지토리 확인하고 작업하셈]** 한 문장으로 재개. 반드시 main의 WORKER_START_HERE.md와 최신 docs/17_NEXT_TASK.md를 먼저 읽는다.
