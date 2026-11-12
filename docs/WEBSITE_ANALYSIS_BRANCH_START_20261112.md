# REA_Web 웹사이트 분석 복원 개발 브랜치 (2026-11-12 KST)

- Branch: `feature/website-analysis-rebuild`; parent source `feature/d27-windows-python-discovery@97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d`. 신규 브랜치 생성은 원본 Pro 코드의 검증·복구 기준을 바꾸지 않는다.
- Product identity: [최종설계](ORIGINAL_FINAL_DESIGN.md) · [REQUIREMENTS](../REQUIREMENTS.md). 승인된 URL/스크린샷/사용자영상 → Fable5.1 → Astra P4 evidence review → **인간 승인** → 고객 소유 데이터 기반 독립 웹앱 → synthetic+browser E2E.
- 원래 `main`은 docs 기준, 기존 Pro 소스·기능 `feature/d27-windows-python-discovery` 보존, `feature/orchestrator`의 Fable+Astra adapter와 import branches는 필요 원본 검증 후 선별 통합. 전체 브랜치 자동 병합·옛 웹 UI 복제 금지.
- 본 브랜치 현 단계 **설계·브랜치 구성만 완료**; 신규 웹사이트 관찰·Astra E2E·Windows/CI 실행 NOT RUN. 기존 Pro의 합성 tests가 URL→사이트 재구축 성공을 증명하지 않는다.
- 복구: 부모 SHA `97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d`; 신규 요구 설계는 원본 main `docs/ORIGINAL_FINAL_DESIGN.md`; 기존 PR·코드 보존.
- 첫 구현 단위: GitHub source tree에서 `rea/orchestrator.py`, `rea/adapter/fable_to_astra.py`, Fable85/ASTRA partial contract 실제 수용·출력 확인 → 합성 승인 local HTML fixture 1종 → observer→review (HOLD)→실제 Pro 신규 ZIP→Chromium E2E. 제3자 네트워크·실고객/유료 API·배포 금지.
- 현재 원래 REA_Web **최종상품률 UNASSESSED**; 50% milestone까지 근거 없는 점수 부여 금지. 새 `hibi89/data2web_studio`에 Lite 이관·XLSX/TSV 추진.
