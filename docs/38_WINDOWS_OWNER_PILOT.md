# REA_Web D19 — 합성 데이터 전용 Windows 사용자 파일럿 키트

## 목적

비개발자 Windows 사용자에게 추후 직접 검증을 요청할 때 사용할 **검증 가능한 예제 패키지**를 만듭니다. D18의 개발자 CI 통과와 실제 사람의 사용성 검수를 구분합니다. 이 ZIP은 **상용 납품물이나 설치 프로그램이 아닙니다**.

## 설계 선택

- **A 채택:** 표준 Python + ZIP, 2개의 고정 합성 예제(CSV 3행 + JSON 2행), 이미 생성된 웹앱 ZIP과 해시, Windows 사용 절차, 헤더만 존재하는 사람 검수 결과/시간 기록지. 자동 설치/외부 전송 없이 로컬에서 수동 실행.
- **B 보류:** 자체 서명/업데이트 포함 단일 EXE, 자동 설치기, 클라우드 배포. 라이선스·서명·유지보수와 제3자 권리 확인이 선행되어야 함.

## 패키지 내용

`scripts/d19_owner_pilot.py`의 `build`는 외부 CSV/JSON 경로를 받지 않습니다. 딱 다음 7개 항목만 결정론적 ZIP에 담습니다.

| 파일 | 용도 |
| --- | --- |
| `sources/qa_guided.csv` | 저장소 고정 SHA 합성 3행 |
| `sources/qa_pair_extra.json` | 저장소 고정 SHA 합성 2행 |
| `demo/approved_pair.zip` | 동일 스키마 APPROVE+APPROVE+APPEND를 통한 5행 읽기 전용 앱 |
| `MANIFEST.json` | 파일별 bytes·SHA256, `NOT_RUN` 인간 검수 상태 |
| `README_WINDOWS.txt` | 체크→실행→5행·검색·필터·상세 확인→Ctrl+C 순서 |
| `HUMAN_PILOT_BLANK.csv` | 사람 검수 결과를 **기입하지 않은** 헤더 |
| `MANUAL_TIME_LOG_BLANK.csv` | 실제 작업 시간/경제성 실측을 **기입하지 않은** 헤더 |

모든 ZIP 멤버·해시·파일 크기를 체크하고, 내부 `approved_pair.zip` 자체의 SHA 원본 증명과 3+2 APPEND 영수증을 재검사합니다. 정상 데이터와 문서를 교체하지 않으며, 기존 출력이 있으면 덮어쓰지 않습니다.

## 개발자 전용 확인 명령

```powershell
python -m scripts.d19_owner_pilot build --out "$env:TEMP\rea-d19-owner-pilot.zip"
python -m scripts.d19_owner_pilot verify --zip "$env:TEMP\rea-d19-owner-pilot.zip"
```

Linux CI는 `/tmp/rea-d19-owner-pilot.zip`으로 별도로 테스트합니다. 사용자에게 필요한 파일은 GitHub Actions의 합성 전용 artifact로만 저장합니다. 앱 자체의 Python 런타임, 의존 라이브러리, 원본 고객 데이터는 포함하지 않으며 자동 네트워크 호출/설치를 하지 않습니다.

## 검증 경계

- CI: 결정론성, 정확한 파일 구성, 고정 공개 합성 소스 해시, 5행 APPEND, 무결성 검사, 기존 출력 불변, 위변조·가짜 사용자 결과 거부, Linux/Windows 회귀 테스트 및 D18 localhost API 검증
- 실제 비개발자 Windows 사용성: **NOT_RUN**. 테스트 실행자는 사용자의 PC에서 직접 실행하고 실제 결과를 기록해야 하며, 자동으로 PASS를 기입하면 안 됩니다.
- 사업화: 원본·분석 대상의 사용 권리, 제3자 소스/패키지 NOTICE, 개인정보·백업·보안, 3건 수동 작업 시간, 300,000원 동일 스키마 APPEND 계약·지원·환불 등 G5/G6 **BLOCKED**. 프로덕션/베르셀은 **미적용**.

## CI 기록

코드 및 문서 초기 작성 이후 정확히 검증된 HEAD·Actions 결과를 `STATUS.md`와 `HANDOFF.md`에 기록합니다. 문서만으로 배포 및 사람 검수를 통과했다고 해석하지 않습니다.
