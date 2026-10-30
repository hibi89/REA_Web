# REA_WEB 런타임 라이선스·취약점 대조 기록 — 2026-10-31 KST

**실측 증거 정리 완료 / 상용 배포 허가 아님.** 코드 테스트 SHA: `bbf2ec26923c0c6dc84a1263780f9e8e5b13fdf5`, [D12](https://github.com/hibi89/REA_Web/actions/runs/41099504228) 및 [D31](https://github.com/hibi89/REA_Web/actions/runs/41099504223) Windows/Linux Actions 성공.

- 실제 GitHub Actions 산출물 4개를 다운로드하고 D12 설치 배포판 메타데이터·라이선스 파일 SHA256과 D31 `pip-audit.json`을 교차검증했다. 아티팩트 ID/파일 지문은 [증거 원장](../evidence/rea_runtime_licenses_20261031_bbf2ec.json)에 기록했다.
- Windows Python 3.11.9, Linux Python 3.11.17 환경에서 **14개 배포판 이름과 버전 14/14 일치**, 각 14개 라이선스 파일 확인.
- D31 `pip-audit`의 발견된 취약점 보고는 Windows 0건, Linux 0건. **스캔 시점 매칭 결과일 뿐 보안 보증이 아니다.**
- D12 감사 결과 `EXTRAS_NOT_FULLY_EXPANDED`; optional extras에 대한 완전한 의존성 해결 감사가 아니다.
- 고객용 ZIP에는 라이브러리 wheel·Python 실행기가 없고 `fastapi>=0.110,<1`, `starlette>=1.3.1,<2`, `uvicorn>=0.27,<1` 설치 범위만 포함한다. 고객 PC와 CI 결과가 반드시 동일한 설치본이라는 뜻은 아니다.

## 14개 패키지 실제 메타데이터 비교

| 배포판 | 확인 버전 | 라이선스 선언 (설치 메타데이터) | LICENSE 지문 Windows / Linux (SHA256 앞 12자리) |
|---|---:|---|---|
| `annotated-doc` | `0.0.5` | MIT | `fff170779a6a` / `fff170779a6a` 일치 |
| `annotated-types` | `0.8.0` | MIT | `fe1049884b1a` / `fe1049884b1a` 일치 |
| `anyio` | `4.15.1` | MIT | `5361ac9dc58f` / `5361ac9dc58f` 일치 |
| `click` | `8.5.0` | BSD-3-Clause | `9a8ad106a394` / `9a8ad106a394` 일치 |
| `fastapi` | `0.162.0` | MIT | `4ec89ffc8148` / `4ec89ffc8148` 일치 |
| `h11` | `0.16.0` | MIT (legacy field) | `37db5bb85926` / `37db5bb85926` 일치 |
| `idna` | `3.20` | BSD-3-Clause | `1a9a4f0e3d47` / `1a9a4f0e3d47` 일치 |
| `opentelemetry-api` | `1.45.2` | Apache-2.0 | `c71d239df917` / `c71d239df917` 일치 |
| `pydantic` | `2.14.2` | MIT | `a9e186f3ca16` / `a9e186f3ca16` 일치 |
| `pydantic-core` | `2.50.2` | MIT | `fbe7f615f18d` / `2afdd30d54b4` **서로 다름** |
| `starlette` | `1.10.0` | BSD-3-Clause | `dcb95677a022` / `dcb95677a022` 일치 |
| `typing-extensions` | `4.16.0` | PSF-2.0 | `3b2f81fe21d1` / `3b2f81fe21d1` 일치 |
| `typing-inspection` | `0.4.4` | MIT | `804b59b25f2c` / `804b59b25f2c` 일치 |
| `uvicorn` | `0.54.0` | BSD-3-Clause | `efe1acf3e62f` / `efe1acf3e62f` 일치 |

## 확인된 차이

`pydantic-core==2.50.2`의 Windows/Linux 라이선스 파일 지문은 서로 다르다. 플랫폼별 wheel 내용 차이 등의 가능성은 있으나 원인과 라이선스 고지 의무는 **미확인**이다. 이것만으로 라이선스 위반이라고 결론 내리지 않는다. 나머지 13개 파일의 지문은 일치한다.

## 실제 출시 전 필요한 판정

1. 생성 코드·템플릿과 기여자에 대한 소유·납품 권한 확인. Fable/Astra 소스는 고객 ZIP에서 제외되지만 분석 도구 사용과 코드 권리를 별도로 확인할 것.
2. 고객용 Windows 버전을 재현 가능하게 고정하고 공식 wheel에서 **각 LICENSE/NOTICE 원문과 고지 의무**를 사람의 검수로 확정. 현재 메타데이터 지문은 법률 검토와 정규 wheel 해시를 대체하지 않는다.
3. 실제 고객 동의·비민감 입력·ZIP 평문 SQLite 취급·삭제/보관, 인간 Windows 검수, 판매가격/수정/환불/지원 조건 승인과 실제 작업시간 3건 실측. **현재 모두 출시 차단 유지.**

**분류:** 개발자 CI 재현 환경의 증거만 검증. 고객용 ZIP·원본 소스·권한·서비스 배포 변경 없음. 배포 승인: `NOT_GRANTED`, 사용자 Windows: `NOT_RUN`.
