> **2026-10-28 해총 최종 공통 개발·검증 지시 / 소유자 최신 결정:** [전 프로젝트 개발 속도·검증 통합 정본](https://github.com/hibi89/hackathon-command-center-2026/blob/main/docs/DEV_ACCELERATION_AND_VERIFICATION_20261028.md). 현재 **KIC(+DL)·PayPal·UGREEN·LA만 활성 4개 작업 슬롯**, 이 브랜치는 **임시 대기(원본 보존, 폐기 아님)**. 다른 소유자 지시로 재개되지 않았다면 `ㄱ`만으로 자율적인 코드 수정/테스트 CI/배포를 시작하지 않는다. 재개 시 합의된 구현은 GPT-6 **Instant**, 최초 설계·난제·해총 최상위 검수는 높은 추론; 실제 기능 중심, GitHub 파일 단위 반복·다중 상태문서 복제·동일 SHA CI 폴링 줄임. 단일 안전 로컬 검증과 정확한 실행 SHA/PASS·FAIL·SKIP을 보고한다. 기존 제품 설계·권리·보안·사용자 승인·동결/복구·비공개 원본 보호 규칙은 보존한다. 본 공지는 개발 허가나 테스트 통과 주장 아님.

# REA_Web — engineering agent policy (canonical)

Read `WORKER_START_HERE.md` and `docs/SESSION_RESTART_PROTOCOL.md` first, followed by remote `STATUS.md`, `HANDOFF.md` and `docs/17_NEXT_TASK.md`. Use latest actual GitHub state, not previously written chat assumptions.

**Restart trigger:** `[REA_Web 깃헙 레포지토리 보고 작업이어가셈]` means **inspect repository and execute next safe READY task immediately**. It already has the meaning of `ㄱ`. Do not ask user to resend ZIP, choose branch, confirm the existing design or approve normal synthetic development. User specifically wants completed work, not status-only replies.

Project: integrate Fable 5.1 analysis with Astra Web Catcher evidence/functional spec and an independently generated customer-data-based webapp. Current MVP already generates readonly FastAPI/SQLite from UTF-8 CSV; next unit is the adapter. Main is not a runnable integration checkout yet.

Development order: real MVP -> compare target architecture -> fill gaps -> robust tests and sale readiness. Three-day completion is a stretch goal. Respect evidence/permission boundaries and strictly limited 300,000 KRW product; no mandatory collecting customer data or touching live DB.

**Branch discipline:** Do not modify upstream Fable/Astra repositories or pinned import branch snapshots. Work on dispatch target branches, preserve existing unique commits, and maintain Draft PRs until verification. Don't merge incomplete source snapshots blindly. Status-only edits never count as implementation.

**Truthful QA:** capture tested SHA, exact command, OS, PASS/FAIL/SKIP. No unrun claim, silent approval, production deployment, customer data, credentials or payment/complex-auth integration. Non-deferable protection: no overwrite, bounded inputs, safe escaping, parameterized SQL, localhost-only. Advanced security reviews can be late, but are needed before real customer deployment.

**Handoff:** After each unit update main STATUS/HANDOFF/NEXT_TASK; if some writes blocked by conflicts, report precisely and proceed safely. Two repeated failures => switch approach. If a task is blocked for owner approval, mark it BLOCKED and work on next safe independent item. Next reply must be a substantive development result, not another request for permission.
