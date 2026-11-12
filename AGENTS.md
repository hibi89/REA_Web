> **[OWNER-FINAL-BLUEPRINT-100 | 2026-11-13 KST | 사용자 확정]** 공식 최종완성률은 **사용자 최종설계도 전체 = 100%** 기준으로만 산정. 작업자·총괄이 임의 설계 범위·가중치·수용조건 축소/수정 금지. 해커톤 MVP, 합성/CI, P85/P95 같은 기술 마일스톤을 공식 최종완성률로 부르면 안 된다. 최종설계 요구 ID→소스→정확 SHA 검증·미검증→승인 가중치 100점 추적표와 대조. 근거가 없으면 공식 `UNASSESSED(재산정 대기)`; 과거 수치는 내부 역사 지표로 보존. 해총 `kmong-productization` 최종완성률 원장에 결과 동기화. 기존 [작업중]/등록이력·RELEASE HOLD 변경 금지. [공통 정본](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/strategy/FINAL_BLUEPRINT_COMPLETION_STANDARD_20261113.md). 정책 커밋은 기능 완료나 점수 확정이 아니다.

> **2026-11-13 KST 최우선 검증 현황:** 사용자 요청 원래 REA_Web 85% 단계는 **합성 사이트 3종의 desktop/mobile 실제 Chromium 연속3동작→Astra P4 observed/evidence/review, Pro 새 앱 기능 브라우저 비교, RGB 시각차이 보고 및 보안 거부**로 수용. 정확 CI SHA `1c3390fa3da933c5d0513196f0dcfc97b18b5e14` [Windows/Ubuntu #43273324679](https://github.com/hibi89/REA_Web/actions/runs/43273324679) **각52PASS/0FAIL, 2/2 SUCCESS**. 엔지니어링 **85% 잠정**, 실제 임의 웹사이트의 UI·비주얼/고급 동작 복원과 고객 인수·사용권은 여전히 미검증, RELEASE HOLD. 검증 후 현 P85 `[작업중]` 해제, 새 P95/100 자동 목표 금지. 원본 Fable --record 미통합 및 실제 고객 권한 승인 아님. [검증 보고](https://github.com/hibi89/REA_Web/blob/feature/website-analysis-rebuild/docs/WEBSITE_P85_RESPONSIVE_ACCEPTANCE_20261113.md). DATA2WEB 별도, 기존 Pro/Fable/Astra 소스·타 채팅 작업 표시 불변.

> **2026-11-13 KST 최신 개발 기준:** 원래 웹 분석 REA_Web의 P70 **합성 로컬 3사이트 실제 Chromium/Astra/Pro 수용 게이트 70% 엔지니어링 잠정 달성**, 검증 SHA bfac1116ac7a20c7162f42a59e51277d402b24d9 및 [2/2 GitHub Actions SUCCESS](https://github.com/hibi89/REA_Web/actions/runs/43266467950). 원본 Fable5.1은 정적 스캔만, P70 동작 관찰은 별도 Chromium observer이며, 합성 owner approval은 실제 웹사이트/콘텐츠 권리 승인으로 간주하지 않는다. [상세 증빙](https://github.com/hibi89/REA_Web/blob/feature/website-analysis-rebuild/docs/WEBSITE_P70_BROWSER_ACCEPTANCE_20261113.md). 실제 고객/임의 외부 URL·원 사이트 디자인 재구축·판매/Production HOLD. 사용자 새 단계 목표 전 P85/100 임의 생성하지 않으며 DATA2WEB·원본 브랜치 보존. 과거 아래 UNASSESSED 문구는 P70 검증 이전 역사 상태다.

> **2026-11-12 사용자 최신 재개 지시: REA_Web 전담 웹서비스 분석·재구축 브랜치** — `feature/website-analysis-rebuild`는 [최종설계](docs/ORIGINAL_FINAL_DESIGN.md)/[REQUIREMENTS](REQUIREMENTS.md)를 정본으로 사용. 과거 10/28 대기 지시는 본 제품에 대해 사용자 새 재개 지시로 대체. 기존 Pro/Fable/Astra 소스, 고객 데이터, Lite history 변경 금지. Lite → 독립 `hibi89/data2web_studio`. **원래 웹 분석 최종상품률 UNASSESSED**, 사용자 단계 승인·검증 전 임의 95/100 표시·판매 금지, RELEASE HOLD. `[작업중]`은 확정 목표 미달이면 종료해도 유지.

# REA_Web — engineering agent policy (canonical)

Read `WORKER_START_HERE.md` and `docs/SESSION_RESTART_PROTOCOL.md` first, followed by remote `STATUS.md`, `HANDOFF.md` and `docs/17_NEXT_TASK.md`. Use latest actual GitHub state, not previously written chat assumptions.

**Restart trigger:** `[REA_Web 깃헙 레포지토리 보고 작업이어가셈]` means **inspect repository and execute next safe READY task immediately**. It already has the meaning of `ㄱ`. Do not ask user to resend ZIP, choose branch, confirm the existing design or approve normal synthetic development. User specifically wants completed work, not status-only replies.

Project: integrate Fable 5.1 analysis with Astra Web Catcher evidence/functional spec and an independently generated customer-data-based webapp. Current MVP already generates readonly FastAPI/SQLite from UTF-8 CSV; next unit is the adapter. Main is not a runnable integration checkout yet.

Development order: real MVP -> compare target architecture -> fill gaps -> robust tests and sale readiness. Three-day completion is a stretch goal. Respect evidence/permission boundaries and strictly limited 300,000 KRW product; no mandatory collecting customer data or touching live DB.

**Branch discipline:** Do not modify upstream Fable/Astra repositories or pinned import branch snapshots. Work on dispatch target branches, preserve existing unique commits, and maintain Draft PRs until verification. Don't merge incomplete source snapshots blindly. Status-only edits never count as implementation.

**Truthful QA:** capture tested SHA, exact command, OS, PASS/FAIL/SKIP. No unrun claim, silent approval, production deployment, customer data, credentials or payment/complex-auth integration. Non-deferable protection: no overwrite, bounded inputs, safe escaping, parameterized SQL, localhost-only. Advanced security reviews can be late, but are needed before real customer deployment.

**Handoff:** After each unit update main STATUS/HANDOFF/NEXT_TASK; if some writes blocked by conflicts, report precisely and proceed safely. Two repeated failures => switch approach. If a task is blocked for owner approval, mark it BLOCKED and work on next safe independent item. Next reply must be a substantive development result, not another request for permission.
