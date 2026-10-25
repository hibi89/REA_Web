# REA_Web D17 — Windows 새 가상환경 최초 실행 재현

## 무엇을 실제 확인하는가

D16 Windows launcher는 Python 3.11+, Tk와 이미 설치된 FastAPI/Uvicorn/Pydantic이 필요합니다. D17은 **GitHub Actions의 Windows 개발자 CI에서만**, 독립적인 새 Python 가상환경으로 시작하여 다음 상태 변화를 검증합니다.

1. 소스 코드, launcher, 합성 CSV/JSON 두 개만 임시 폴더로 복사. 실제 고객 파일/환경 변수/비밀키/벤더 원본/레포 전체는 복사하지 않습니다.
2. 새 venv(시스템 site-packages 연결 FALSE)만 준비. 설치 전 해당 폴더의 실제 `START_REA_CREATOR.cmd --check`가 **MISSING_MODULES / 종료코드 11**로 실패해야 합니다.
3. CI 작업자가 분리된 venv에서 명시적으로만 `python -m pip install --no-input "fastapi>=0.110,<1" "uvicorn>=0.27,<1" "pydantic>=2.6,<3"` 수행. 이 CI 전용 Python 패키지 설치에는 네트워크가 필요할 수 있지만, 고객에게 배포하는 CMD/GUI는 자동 설치나 네트워크 호출을 실행하지 않습니다.
4. 동일한 CMD `--check`가 READY / 종료코드 0로 성공. 실제 Tk 창에서 2파일 GUI의 원본 검사, id/title/category 지정, 파일마다 APPROVE 및 최종 APPEND, 로컬 ZIP 생성과 SHA/원본 보존까지 합성 테스트.
5. 민감 경로나 환경설정/설치 로그를 포함하지 않는 상태 JSON만 Actions artifact로 기록하고 테스트 임시 디렉터리 전체 삭제. PASS는 개발자 CI 재현성일 뿐 실제 고객 사용성 검수가 아닙니다.

검증 스크립트: `scripts/d17_windows_fresh_venv.py` (고객용 런처에 연결되지 않은 **개발 테스트 전용**), `.github/workflows/rea-d17.yml`.

## 직접 실행하는 사용자를 위한 설명

Python/Tk가 없으면 공식 경로로 Python을 먼저 설치한 다음 설치가 확인된 사용자 환경에서 안내에 따라 종속 패키지를 수동으로 설치합니다. 프로그램이 자의로 설치하지 않습니다. 재사용할 가상환경을 이미 갖춘 경우 그 환경을 보존하며, 작업 폴더에서 다음 확인을 수행할 수 있습니다.

```bat
START_REA_CREATOR.cmd --check
```

- `MISSING_MODULES (11)`: 해당 환경에 Python runtime 패키지가 없음. PATH를 전역 수정하거나 관리자 권한을 요청하지 마십시오.
- `READY (0)`: 설치된 모듈과 현재 Tk 화면 구성에 대한 실행 전 확인일 뿐 라이선스, 개인정보, 실제 앱 납품 완성이나 기술지원 보증은 아님.
- `TK_UNAVAILABLE (12)`: 현재 Windows 그래픽 화면/GUI 인터프리터 상태가 지원되지 않음. CLI는 별도로 사용 가능.

프로젝트의 실제 사용자 데이터와 ZIP `data.sqlite`는 사용자가 통제해야 합니다. 두 파일을 선택하면 오직 **동일 스키마 ROW APPEND**, 서로 다른 테이블 JOIN은 불가합니다.

## 아키텍처 결정

- **선택 A:** 제한된 CI 새 venv 검증 + 수동 설치 지침. 기존 Windows CMD/GUI와 설치 금지 정책을 그대로 유지.
- **보류 B:** Python 포함 단일 EXE, 자체 패키지 자동 설치 또는 서명 없는 바이너리 배포. 타사 라이선스/NOTICE, 보안, 배포·업데이트·사용자 지원 부담으로 아직 승인하지 않음.

## 출시 차단 조건

상용 G5/G6는 BLOCKED: 실제 승인된 고객 또는 참고자료, 본인의 데이터 처리 권한, 3회 실작업 시간 측정, 라이선스/NOTICE와 재배포 권리, 개인 정보·백업·복구·보안, **비개발자 실제 Windows PC** 설치/접근성, 300,000원 동일 스키마 APPEND 계약 및 지원·환불 조건. CI 통과 여부와 별개로 검증·승인이 필요합니다.
