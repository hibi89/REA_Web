# 크몽 상품 출시 게이트 (2026-10-30) — 승인 전 문서

## Follow-up verification state (2026-10-30, exact feature HEAD)

- Current branch HEAD `64b28c986618c68472649474c6604c2b1fce7372`; latest source compare reports 5 commits ahead / 0 behind `db6711e`.
- GitHub CI connector returned 27 completed successful workflows, including D27 Windows, D26, D24, D6, D3, D9, D20, D22 and D23. The connector response is first-page-only and omits one expected run; exact 28/28 remains unconfirmed.
- Customer preflight now enforces lower and exclusive upper package versions for FastAPI, Starlette, and Uvicorn. Latest isolated guidance tests 18 PASS. Local full suite is incomplete in the managed Windows sandbox due repeated WinError 5 on atomic file publication; D27/D26 targeted tests include 9 such blocked failures.
- Existing three Windows sample packages pass CRC but predate source `f6e34f6`; rebuild them at exact 64b before using them as current-head evidence. Human acceptance remains NOT_RUN; commercial source/vendor and dependency rights remain NOT_GRANTED; customer permission/privacy review and sale terms remain NOT_APPROVED.
- Local update did not move the feature branch. An incomplete connector-created helper branch exists and must not be used as a source branch.

**현재 상태: NOT APPROVED FOR LISTING OR ORDER INTAKE.** 이 문서는 승인·법률 의견·고객 수락을 뜻하지 않는다.

## 현재 코드·검증 기준

- 저장소 `hibi89/REA_Web`, 브랜치 `feature/d27-windows-python-discovery`, 정확한 최신 HEAD `578442b2bd22bb64a004e77bbd091a17930f614a`.
- 최신 HEAD의 GitHub CI **28/28 SUCCESS**: D27 Windows/Linux 전체 회귀, D6 공급망/보안 검사 포함. PR #30은 OPEN/DRAFT/UNMERGED.
- 생성 런타임은 FastAPI/Starlette/Uvicorn을 사용하며 Starlette 하한은 `>=1.3.1,<2`. 고객 사전검사가 낮은 버전을 차단하고 `python`/Windows `py -3` 복구를 안내한다.
- 지원 흐름: 고객 권한이 있는 UTF-8 CSV 또는 flat JSON 배열 → 미리보기와 명시적 필드 매핑 승인 → 로컬 읽기 전용 FastAPI/SQLite 앱 → 목록·검색·카테고리 필터·상세 → Windows 납품 ZIP. 동일 스키마 2파일은 둘 다 별도 승인된 경우 ROW APPEND. 서로 다른 테이블의 자동 JOIN은 미지원.
- 자동 합성 Windows/Chromium 검증은 PASS이나 비개발자 사람의 Windows 검수는 **NOT_RUN**. 상용 코드/의존성 권리는 **NOT_GRANTED**. 개인정보·보존·백업 운영은 **NOT_APPROVED**.
- 기능 개발률 **95%**, 판매 준비율 **77%**는 근거 기반 추정치이며 상품 승인이나 완료 보증이 아니다.

## 크몽 등록 초안에 허용된 범위

- 목표가 299,000원은 미승인 가격 가설이다. 실제 가격·납기·파일/행/열/용량 제한 및 기능 수는 주문 전 데이터 구조를 확인하고 별도 합의한다.
- 합의한 목록·검색·필터·상세 등 구현된 읽기 기능, 실행 ZIP, 한국어 안내 및 검수표.
- 고객이 소유 또는 사용할 권리가 확인된 비민감 자료만 취급한다. 동의 없는 고객 데이터 사용을 가정하지 않는다.
- 제외: 서로 다른 스키마 JOIN, 크롤링/데이터 수집 대행, 외부 사이트 복제, 운영 DB/API, 로그인/권한, 결제, 데이터 수정·삭제(CRUD), 호스팅, 자동 동기화, 민감정보, 무제한 수정, 장기 유지보수.

## 주문 전에 확정·기록할 거래 조건

데이터 형식과 권리, 필드 매핑, 구체 화면/기능, 용량 상한, 납기 시작일과 고객 자료 지연 시 처리, 검수 기준, 무상 결함 수정의 기간·대상, 별도 견적 범위, 소스 제공 여부, 산출물 사용·수정·재배포 권리, 지원 기간/채널, 취소·환불 조건을 서면으로 협의하고 크몽 메시지에 남긴다.

수수료는 서비스 유형과 카테고리에 따라 달라질 수 있다. 299,000원에서 판매자 실수령액을 추정하거나 보장하지 말고, 전문가 계정의 크몽 수익금 계산기에 등록 카테고리와 거래 금액을 넣어 확인한다. 세금 처리는 판매자 등록 자격과 실제 거래 자료에 따라 확인한다.

작업물은 크몽 작업물 발송을 이용해 전달한다. 최신 서비스 이용약관은 구매확정 전 확인·수정요청 기간과 자동 구매확정 절차를 규정하며 법정 예외 조항도 둔다. 판매자는 상세페이지/주문 시점의 적용 약관과 법을 다시 확인하고, blanket refund/수정 보장 또는 포기 문구를 임의로 만들지 않는다.

## 릴리스 차단 항목 (현재 미완료)

- 저장소 코드, Fable/Astra 포함 공급 코드, Python 및 FastAPI/Uvicorn 및 모든 전이 의존성의 상업 사용·재배포 권리와 필수 LICENSE/NOTICE 검토: **NOT_GRANTED**.
- 비개발자 일반 Windows 사용자 설치/더블클릭/복구/재실행/백업 인수 검수: **NOT_RUN**.
- 실제 고객 데이터 권리·동의 시험, 개인정보/보안/보존/삭제/백업 정책 검토: **NOT_RUN**.
- 실제 작업 시간 측정, 전문가 계정 카테고리 수수료/실수령 확인, 가격·납기·지원·수정·환불 조건 승인: **NOT_APPROVED / NOT_RUN**.

## 공식 크몽 문서

- [신규 전문가를 위한 판매 가이드](https://kmong.com/support/expert-center/posts/766) — 사전 거래 조건/작업물 발송/세금계산서 주체 관련 안내.
- [판매 데이터 관리 방법](https://kmong.com/support/expert-center/posts/687) — 범위·일정·견적을 서비스 설명/메시지에서 협의하는 안내.
- [수익 관리와 수익금 계산기](https://support.kmong.com/hc/ko/articles/39865769064217--%EC%9D%B4%EC%9A%A9-%EB%B0%A9%EB%B2%95-%EC%88%98%EC%9D%B5-%EA%B4%80%EB%A6%AC%EB%8A%94-%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80%EC%9A%94) — 카테고리 및 거래 금액 입력 안내.
- [서비스 이용약관 2026-01-28 ver.](https://support.kmong.com/hc/ko/articles/54222204542233-%EC%84%9C%EB%B9%84%EC%8A%A4-%EC%9D%B4%EC%9A%A9%EC%95%BD%EA%B4%80-2026-01-28-ver) — 구매확정 및 청약철회 관련 적용 문구; 주문 시점에 최신 본문 재확인 필요.

PR #30 stays open, draft and unmerged. This document does not authorize sale, merge, or customer data use.
