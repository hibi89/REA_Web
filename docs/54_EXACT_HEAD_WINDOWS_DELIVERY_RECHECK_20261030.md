# D27 정확한 HEAD Windows 납품 재검수 (2026-10-30)

## 원격 상태

- 저장소: `hibi89/REA_Web`, 브랜치 `feature/d27-windows-python-discovery`
- 작업 시작 시 확인한 HEAD: `136e0234c5247c633fb2706fc57f2027418f1a86`
- PR #30: OPEN / DRAFT / UNMERGED.
- 해당 HEAD의 GitHub Actions workflow-run 조회 결과: 반환된 28개 run 전부 SUCCESS. 자동 합성 검증이며 비개발자 고객 검수는 아니다.

## 정확한 HEAD 로컬 재검수

보존된 exact-head 작업 복제본에서 synthetic fixture만 사용했다. 원본 CSV/JSON 해시를 보존한다.

- `tests/test_customer_guidance.py tests/test_d27_python_discovery.py`: 시스템 Temp에서는 18 PASS / 3 FAIL. 세 실패 모두 코드 assertion 전 Windows 샌드박스가 Temp의 `os.rename`을 `WinError 5`로 차단했다.
- 동일 테스트를 허용된 작업공간 Temp로 설정해 재실행: **21 PASS**.
- D9 two-source + boundaries: **15 PASS / 2 DESELECTED**. 제외된 사례는 TestClient HTTP 대기 및 symlink 권한 의존 항목.
- 정확한 HEAD 코드로 CSV와 flat JSON 납품 ZIP을 각각 새로 생성, CRC 확인, 한글 폴더 경로로 압축 해제, 실제 `cmd.exe /d /c check_windows.cmd --check` 실행: 두 패키지 모두 **PASS**. 두 ZIP 모두 16개 항목이며 고객 데이터가 아닌 합성 fixture다.
- 생성 ZIP의 `README_WINDOWS.md`, `ACCEPTANCE_CHECKLIST.md`, `launch_windows.cmd`, `check_windows.cmd`, `self_check.py`를 확인. 사전검사 문구는 로컬 prerequisites PASS와 상용 권리 NOT_GRANTED/인간검수 NOT_RUN을 구분한다.
- 압축 해제 후 생성 앱 핸들러를 직접 호출하여 health/list(3행)/한글 포함 샘플 title search/category filter/detail/404 및 SQLite `quick_check`: CSV·JSON 모두 **PASS**. 이것은 실제 localhost 또는 브라우저 E2E 검증이 아니다.
- Formula-like 입력은 문자열로 유지되고 생성 브라우저 렌더러가 `textContent`를 사용하며 `innerHTML`을 포함하지 않음: 직접 확인 **PASS**.
- 통합 회귀 일부는 결과 요약 없이 정지하여 중단했다. 이 로컬 전체 회귀는 **INCOMPLETE**이며 PASS로 표시하지 않는다. TestClient/ASGI 실행은 sandbox에서 응답을 반환하지 않아 BLOCKED/NOT_RUN. 독립 socket probe의 loopback 연결은 `WinError 10013`으로 차단됐다. GitHub의 Windows CI HTTP 증거와 구분한다.

## 합성 패키지 기록

- CSV ZIP: `REA_Web_synthetic_exact136_verified.zip`, SHA-256 `0d20092e1d2e463b734d635fb2e8ab38d02f432500aac3f40ebb2ad1e5787857`.
- JSON ZIP: `REA_Web_synthetic_json_exact136_verified.zip`, SHA-256 `55327958b64ad23fa5b7c434c46813be8aad8fa33af786ea27d7eec7eee1b587`.
- 두 ZIP은 재현용 합성 QA 산출물이며 고객 납품물이나 판매 승인이 아니다.

## 미해결 릴리스 게이트

- 일반 비개발자 Windows 사용자 acceptance: **NOT_RUN**.
- 원본·Fable/Astra 공급 코드·Python 및 모든 런타임 의존성 상용 재배포 권리: **NOT_GRANTED**.
- 실제 고객 데이터 권한/개인정보 보존·삭제·백업 운영: **NOT_APPROVED**.
- 판매자 계정 수수료·세금·납기·지원·수정·취소·환불 조건 및 299,000원 가격 승인: **NOT_APPROVED**.
- 따라서 제품은 판매 승인 상태가 아니다. 어떠한 외부 승인도 본 자동/로컬 시험으로 추정하지 않는다.
