## 2026-10-31 KST — browser-cache privacy mitigation (NOT privacy approval)

- Source SHA `bbf2ec26923c0c6dc84a1263780f9e8e5b13fdf5` adds local HTTP response `Cache-Control: no-store` / `Pragma: no-cache` / `X-Content-Type-Options: nosniff` / `Referrer-Policy: no-referrer` to discourage browser caching/reference URL leakage and content type sniffing. No secret/customer data was used in development. Isolated synthetic mirror HTTP checks PASS; full new-source CI **PENDING** at initial write.
- These response headers **do not encrypt** the plaintext `app/data.sqlite`, protect ZIP at rest, restrict local user processes, establish authentication, guarantee OS/browser secure deletion, or authorize transfer of real personal information. Existing consent, approved transfer/retention, manual secure handling and sale gates remain **NOT_APPROVED**.
- The old step list below remains required. Do not replace it with "the browser won't retain anything."

# 고객 데이터 처리·보존 검토 — 승인 전

**상태: NOT_APPROVED / NOT_RUN.** 코드 동작 검토 기록이며 개인정보·보안 승인, 법률 의견, 고객 동의를 의미하지 않는다.

## 생성기에서 확인한 데이터 흐름

- CSV/JSON 원본을 읽어 SQLite 데이터베이스와 스키마 요약을 생성하고 결과 앱/ZIP을 만든다. 입력 원본을 덮어쓰거나 삭제하는 생성 동작은 확인되지 않았다.
- ZIP용 임시 작업 폴더는 출력 ZIP 상위 경로에 만들고 Python TemporaryDirectory 종료 시 정리한다. 파일 삭제이지 포렌식 복구를 막는 secure erase 보장은 아니다.
- 납품 ZIP에는 app/data.sqlite가 들어가며 고객 입력 행의 값이 포함된다. ZIP은 암호화되지 않는다. app/manifest.json에는 입력 파일 이름, SHA-256, 필드명과 행 수 등이 들어갈 수 있고 schema preview는 열 이름/요약을 포함한다.
- 실행 앱은 loopback 127.0.0.1 바인딩과 읽기 전용이다. 합성 Chromium 시험에서 외부 요청은 관찰되지 않았으나 모든 고객 PC의 네트워크 행위를 보증하지 않는다.
- 자동 백업/동기화/앱 내 삭제, 인증, ZIP 암호화, PII·비밀정보 스캔, 안전 삭제가 있다고 확인되지 않았다. 민감도 판정은 NOT_ASSESSED다.

## 판매 전 데이터 최소화 절차 초안

1. 원본 수령 전에 권리·사용 목적을 확인한다. 가능하면 실제 데이터 대신 열 이름 및 합성/비식별 샘플로 스키마를 협의한다.
2. 민감정보, 인증 토큰, 비밀번호와 권리 불명 자료는 기본 범위에 포함하지 않는다. 자동 탐지된다고 약속하지 않는다.
3. 거래 전 자료 전달 경로, 접근자, 작업 폴더, 보관 기간, 백업과 삭제 조건을 서면으로 합의한다. 승인되지 않은 별도 채널로 파일을 옮기지 않는다.
4. 원본을 임의로 삭제하거나 secure erase를 주장하지 않는다. 임시 파일 정리는 고객의 보관 조건을 확인하고 증거를 기록한다.
5. 고객에게 결과 ZIP에 SQLite 데이터가 평문으로 들어 있다는 점을 알리고 암호화 ZIP으로 오인시키지 않는다. 고객이 지정/승인한 전달 경로를 사용한다.
6. 판매자 PC의 원본, ZIP, 백업과 오류기록의 보관 사유/기간을 거래별로 기록한다. 현재 자동 보존·삭제 시스템은 확인되지 않았다.

## 판매/작업 시작 전 승인 게이트

- [ ] 실제 고객 동의, 데이터 목적과 최소수집 범위 승인
- [ ] 결과 ZIP에 고객 행이 포함되며 암호화되지 않는다는 안내 승인
- [ ] 판매자 작업용 임시본/백업/오류 기록의 접근·보관·삭제 운영 확인
- [ ] 암호화, PII 스캔, 접근통제, secure erase를 지원한다고 오인시키는 문구 제거
- [ ] 코드·의존성 재배포 권리, 개인정보 및 보안 검토 승인

모든 항목은 미완료다. 어떤 고객 자료도 이 검토에 사용하지 않았다.
