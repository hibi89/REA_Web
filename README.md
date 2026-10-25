# REA_Web — 웹서비스 분석·재구축 자동화 엔진

> 2026-10-25 · **3일 MVP 우선 개발 중** · Day1 CSV 웹앱 + Day2 검토용 Fable→Astra 어댑터 구현·CI PASS · 전체 통합 미완성

**새 채팅 즉시 재개:** `[REA_Web 깃헙 레포지토리 보고 작업이어가셈]` — 질문 없이 최신 GitHub 문서·코드 확인 후 다음 READY 개발 작업을 수행한다. **최우선 안내:** [WORKER_START_HERE.md](WORKER_START_HERE.md) · [세션 복원 프로토콜](docs/SESSION_RESTART_PROTOCOL.md).

## 제품 목표
고객이 권한을 가진 참고 웹사이트의 관찰 정보를 Fable 5.1로 분석하고, Astra의 증거·명세·매핑 모듈을 사용해 **고객 제공 CSV/JSON으로 동작하는 별도의 웹앱**을 생성·검증한다. 외부 소스 복제, 숨겨진 서버 로직 추출 또는 무허가 데이터 수집 제품이 아니다.

## 지금 실제로 동작하는 것 (Day1)
- `feature/csv-local-mvp` @ `5515a7286d63211e32d2c577f93f77d61f37ce08`: UTF-8 CSV → 새 SQLite → 독립 로컬 FastAPI 웹앱 (목록·검색·카테고리 필터·상세).
- 실제 GitHub Actions [40198326369](https://github.com/hibi89/REA_Web/actions/runs/40198326369): 9 pytest PASS, Chromium 루프백 E2E PASS (5개 목록, 필터 2, 검색 1, 상세, 새로고침), JS·외부 요청 오류 0건. Windows와 실제 고객 데이터는 미검증.
- [Draft PR #3](https://github.com/hibi89/REA_Web/pull/3) · 미병합. **main은 현재 통합 앱 실행 브랜치가 아니라 프로젝트 명세/인수인계 기준점**이다.

## 코드 및 브랜치
- Fable 5.1 고정 소스 88개: `import/fable51-bbe72c0`, [Draft PR #1](https://github.com/hibi89/REA_Web/pull/1).
- Astra P4 선택 소스 103개(41개 계약 모듈; PARTIAL): `import/astra-p4-b3166b6`, [Draft PR #2](https://github.com/hibi89/REA_Web/pull/2).
- 작업 타깃: `feature/evidence-adapter` (다음 READY), `feature/csv-local-mvp` (Day1), `feature/orchestrator`, `integration/develop`, `qa/cross-platform`.
- 원본 Fable/Astra 소스 저장소는 변경하지 않는다.

## Day2 구현·검증 완료 (feature 브랜치)
- `feature/evidence-adapter` `fda96076de33ebf4f4b6118972a5033a3f703ba9`, [Draft PR #4](https://github.com/hibi89/REA_Web/pull/4).
- 합성 샘플 Fable 결과 → 검토 전용 Astra 증거·명세 제안, 추정/관찰 구분, 승인·생성 차단. GitHub Actions [CI run 40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969): Ubuntu Python 3.11, **28 테스트 통과**, 고정 Astra 계약 모델 검증 및 CLI 통과.
- Day1/Day2 서로 다른 브랜치에서 테스트되었으며 **전체 REA_Web 통합 완료가 아님**.

## 다음 작업 (지금 시작 가능)
`REA-MVP-D2-02`: `feature/orchestrator`에서 선택적 Fable 보고서 + 고객 CSV→로컬 앱 생성 흐름 연결. 그다음 3개 샘플, Windows, 실제 브라우저, 패키징 및 원 설계 차이 검증. **라이브 고객 DB·자동 배포는 제외**.

## 사업/범위
초기 크몽 가격 가설 300,000원. 소규모 고객 제공 CSV 중심, 2개 화면·3개 단순 기능 이내 정액 납품을 목표로 한다. 데이터 수집 대행·운영 DB 접근·복잡한 인증·결제·무제한 수정 제외. 아직 판매 개시/납품 준비가 완료된 상태가 아니다.

**설계도:** [아키텍처](docs/02_ARCHITECTURE.md) · [3일 계획](docs/MVP_3DAY_SPRINT_PLAN.md) · [최종 산출물](docs/14_FINAL_DELIVERABLES.md) · [인수검사](docs/05_ACCEPTANCE.md) · [30만원 범위](docs/07_KMONG_OFFER.md) · [최신 작업지시](docs/17_NEXT_TASK.md).
