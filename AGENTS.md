> **[KMONG_WORK_IN_PROGRESS_20261112 — 크몽 필수 지침 / 소유자 승인]** 이 저장소에서 크몽 상품 또는 육성 후보 작업을 담당하면 새 채팅·`ㄱ` 재개 시 이 `AGENTS.md`를 반드시 읽는다.
> - **실제 상품 개발·수정·테스트/검증 착수 시 즉시:** 중앙 `hibi89/hackathon-command-center-2026`의 `kmong-productization` 브랜치 [최종완성률 및 작업 현황 표](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/audits/KMONG_16_CURRENT_20261111.md)에서 **담당 제품명 바로 옆에 `**[작업중]**`**을 작성하고 실제 GitHub 커밋을 확인한다. 같은 저장소에 상품이 여럿이면 현재 담당 상품만 표시. 활성 16종 외 PREP·FFAX·Factory AX 등의 후보는 같은 문서의 별도 후보 작업 상태 표에서 표시한다.
> - **검증된 목표 완성률 달성 / 종료 / 중단 / 보류 / 다른 상품으로 작업 전환 시 즉시:** 자신의 `[작업중]`만 제거해 GitHub 커밋을 확인한다. 다른 채팅이 작업 중인 표식은 임의 변경하지 않는다. 중앙 최신 HEAD를 먼저 읽고 동시 갱신을 보존한다.
> - 중앙 기록 쓰기 실패 시 제품 `STATUS.md`·`HANDOFF.md`와 답변에 **`KMONG_HUB_SYNC_PENDING`**을 기록한다. 자동 실시간 동기화가 없고, 표식은 완성률 상향·판매/배포 승인이나 작업 자동 실행을 의미하지 않는다. 실제 검증 근거 없이는 숫자를 변경하지 않는다.

# REA_Web — engineering agent policy (canonical)

Read `WORKER_START_HERE.md` and `docs/SESSION_RESTART_PROTOCOL.md` first, followed by remote `STATUS.md`, `HANDOFF.md` and `docs/17_NEXT_TASK.md`. Use latest actual GitHub state, not previously written chat assumptions.

**Restart trigger:** `[REA_Web 깃헙 레포지토리 보고 작업이어가셈]` means **inspect repository and execute next safe READY task immediately**. It already has the meaning of `ㄱ`. Do not ask user to resend ZIP, choose branch, confirm the existing design or approve normal synthetic development. User specifically wants completed work, not status-only replies.

Project: integrate Fable 5.1 analysis with Astra Web Catcher evidence/functional spec and an independently generated customer-data-based webapp. Current MVP already generates readonly FastAPI/SQLite from UTF-8 CSV; next unit is the adapter. Main is not a runnable integration checkout yet.

Development order: real MVP -> compare target architecture -> fill gaps -> robust tests and sale readiness. Three-day completion is a stretch goal. Respect evidence/permission boundaries and strictly limited 300,000 KRW product; no mandatory collecting customer data or touching live DB.

**Branch discipline:** Do not modify upstream Fable/Astra repositories or pinned import branch snapshots. Work on dispatch target branches, preserve existing unique commits, and maintain Draft PRs until verification. Don't merge incomplete source snapshots blindly. Status-only edits never count as implementation.

**Truthful QA:** capture tested SHA, exact command, OS, PASS/FAIL/SKIP. No unrun claim, silent approval, production deployment, customer data, credentials or payment/complex-auth integration. Non-deferable protection: no overwrite, bounded inputs, safe escaping, parameterized SQL, localhost-only. Advanced security reviews can be late, but are needed before real customer deployment.

**Handoff:** After each unit update main STATUS/HANDOFF/NEXT_TASK; if some writes blocked by conflicts, report precisely and proceed safely. Two repeated failures => switch approach. If a task is blocked for owner approval, mark it BLOCKED and work on next safe independent item. Next reply must be a substantive development result, not another request for permission.
