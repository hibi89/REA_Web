# REA_Web — 오프라인 ZIP 복구 (제작자·지원 담당자용)

**상태:** 구현 완료, 분리 Linux 환경의 범위 제한 테스트 PASS. 원본 저장소 전체 CI·일반 사용자 Windows 수락·상용 출시 승인은 미검증.

## 실행

REA_Web 소스 체크아웃 루트의 Python 3.11+ 명령 프롬프트 또는 PowerShell에서:

```powershell
python -m rea.recovery --zip .\owner-original.zip --out .\owner-recovered-new
```

- --zip은 보관 중인 원본 ZIP 파일입니다. 심볼릭 링크/비ZIP 파일을 거부합니다.
- --out은 존재하지 않는 새 폴더입니다. 기존 빈 폴더도 덮어쓰지 않습니다.
- ZIP의 고정된 임시 복사본에 대해 전체 파일 SHA256·의미 검사·승인 기록의 정합성 검사를 수행합니다. 검증한 동일 복사본만 압축 해제합니다.
- 추출 파일 트리, 개별 SHA256, 읽기 전용 SQLite 접근 및 앱 매니페스트 행 수 대 SQLite 행 수를 검사한 뒤 안전한 no-replace 방식으로 새 폴더에 게시합니다.
- 오류 발생 시 새 폴더는 게시되지 않고 작업용 임시 디렉터리만 정리됩니다. 원본 ZIP·기존 폴더를 보존합니다.
- 압축 파일 크기는 최대 약 51MiB로 제한하며, 원래 ZIP 검증기의 100개 멤버·총 25MiB 압축 해제 제한을 따릅니다.

## 범위 및 추가 검사

복구 결과 RESTORED_INTEGRITY_AND_READONLY_SQLITE_ONLY는 파일 해시·SQLite 읽기만 의미합니다. 반환되는 native_windows_launch_accepted=false, python_dependencies_accepted=false, commercial_clearance=NOT_GRANTED는 의도적으로 보수적으로 유지합니다. 고객 PC에서 check_windows.cmd --check, launch_windows.cmd, 브라우저 목록·검색·상세는 별도로 검증해야 합니다. SHA256은 게시자 서명이나 재배포 라이선스가 아닙니다.

도구는 REA_Web 소스에서 실행하는 지원용 CLI이며 납품 ZIP에 자동 포함되지 않습니다. 자동 설치·서버 실행·외부 업로드·원본 변경·기존 폴더 직접 복구 기능이 없습니다.

## 테스트 증거

tests/test_recovery.py: 합성 CSV·JSON·승인된 두 파일 ROW APPEND, 잘못된 ZIP, 잘못된 행 수, 기존 대상 덮어쓰기 방지, 동시 생성 경합, 초과 크기·심볼릭 링크, CLI 결과 회귀 테스트. 최신 원본 저장소 전체 테스트는 아직 미실행입니다. 분리 Linux Python 3.13에서 복구 모듈 Git blob SHA를 검증하고 기존 감사 모듈을 일부 대체한 범위 제한 6/6 테스트를 실행했습니다. 이 결과를 실제 고객 Windows E2E로 표기하지 마세요.

상용 판매에는 별도 독립 사용자 Windows 인수검수, 소스/의존성 상용 재배포 권리, 개인정보·보존·삭제 운영, 판매자 조건 및 실제 사람의 납품 소요시간 증거가 필요합니다. 현재 NOT APPROVED FOR SALE.
