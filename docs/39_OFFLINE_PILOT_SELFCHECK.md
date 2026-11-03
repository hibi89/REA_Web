# REA_Web D20 — Windows 체험 키트 자체 무결성 검사 (오프라인)

## 결정과 목적

D19의 합성 전용 Windows 사용자 체험 패키지는 파일을 직접 압축 해제해 보는 과정을 요구합니다. 여기서 실제 웹앱 실행 이전에 전용 진단기를 실행하여 **압축 해제 후 파일이 원본 키트와 일치하는지** 확인하는 기능을 추가했습니다.

- **A 채택:** Python 표준 라이브러리만 사용하는 읽기 전용 자체검사 스크립트를 D19 합성 ZIP에 포함. 추가 종속성·설치·서명/업데이트 부담 없이 누구나 기존 Python으로 확인 가능.
- **B 보류:** EXE/설치기/자동 업데이트 또는 클라우드 검사. 법적 배포 권리, 서명, 사용권 및 보안·비용 평가가 필요합니다.

## 변경 사항

- `scripts/d20_offline_kit_check.py` 내용을 키트의 `CHECK_PILOT_OFFLINE.py`로 고정 복사. 외부 서버 요청이나 패키지 설치, 자동 웹앱 실행, 파일 수정, 관리자 권한 요구가 없습니다.
- `scripts/d19_owner_pilot.py`: 허용 멤버를 7개에서 **8개**로 확장. 새 검사기 바이트도 manifest의 SHA256으로 기록, 원본이 바뀌면 패키지 생성기에서 거부. 기존 2개 합성 소스·5행·원본 SHA 규칙, 두 승인과 최종 APPEND는 유지.
- 사용자가 ZIP을 **새 폴더에 압축 해제**한 후, 앱 실행 전에 해당 폴더에서 `python CHECK_PILOT_OFFLINE.py` 실행. 출력 `OFFLINE_KIT_INTEGRITY_PASS`는 오직 바이트/구조 일치 증거이며 실제 고객, 합법적 권리, 상용 보안 및 사람 수락의 승인과 **무관**합니다.
- 새 스크립트는 외부/내부 manifest의 멤버 목록·크기·SHA256, 원본 2개 고정 합성 해시, 변조/누락·심볼릭 링크, APPEND 영수증의 3+2행·APPROVE 2회·JOIN 금지, SQLite 헤더, 비어 있는 사람 검수 기록지와 권리 NOT_GRANTED를 확인합니다.
- 검사 성공/실패는 현재 키트의 파일을 변경하지 않으며, 민감한 원본 셀 데이터/경로를 출력하지 않습니다. SHA256은 인증 서명이 아니므로 패키지 전달자를 인증하는 수단이 아닙니다.

## CI 검증

`tests/test_d20_offline_kit_check.py`는 실제 D20 ZIP 압축 해제 후 표준 Python으로 자체검사 실행, 8개 SHA/허용목록, 변조·누락·시스템 링크 거부, 헤더만 존재하는 사람 검수/작업시간 로그 보존, 재현 가능 ZIP, 기존 파일 덮어쓰기 금지와 실행 결과를 검사합니다.

`.github/workflows/rea-d20.yml`은 D19의 Linux/Windows 전체 pytest, 8+3 Chromium, GUI, 새 Windows 가상환경의 GUI→ZIP→127.0.0.1 HTTP와 pinned Fable/Astra SHA 검사뿐 아니라 **압축 해제된 D20 최종 키트의 실제 로컬 자체검사**를 각 OS에서 실행합니다.

실행 결과와 검증 SHA는 실제 GitHub Actions 완료 상태를 확인한 뒤 `STATUS.md`·`HANDOFF.md`에 기록합니다. 단순 코드 존재나 PASS 문자열만으로 성공 주장하지 않습니다.

## 출시 차단

- 실제 비개발자 Windows 사람 검수 및 접근성·시간 기록: **NOT_RUN**
- 실고객/참조 데이터 사용 권리·원본 공개 권리, 세 건의 실제 작업 소요 시간: **BLOCKED**
- 제3자 라이선스/NOTICE/재배포, 개인정보/백업/보안, 30만원 SAME-SCHEMA ROW APPEND 서비스 범위·지원·환불: **BLOCKED**
- Vercel/Production 공개 서비스: **NOT APPLICABLE**
