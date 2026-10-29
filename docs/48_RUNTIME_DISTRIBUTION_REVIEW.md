# 상용 배포 권리 검토 인벤토리 (승인 아님)

이 자료는 Windows 개발 PC에서 수집한 설치 메타데이터를 검토 담당자가 확인할 수 있게 정리한 것입니다. 법률 의견·SBOM/잠금 파일·고객 설치 결과·상용 라이선스 승인이 아닙니다. 현재 결론은 `NOT_GRANTED`입니다.

## 런타임 공급 경계

- 생성 앱은 Python 3.11+와 FastAPI/Uvicorn을 사용합니다. 생성 ZIP의 `app/requirements.txt`는 `fastapi>=0.110,<1`, `uvicorn>=0.27,<1` 범위입니다.
- Windows README는 패키지가 없는 경우 사용자가 선택적으로 동일 Python 인터프리터에 설치하도록 안내하며, 그 설치는 인터넷이 필요할 수 있다고 명시합니다. ZIP에 Python 런타임이나 wheel은 포함하지 않습니다.
- 실제 선택 버전은 고객 PC/PyPI 시점에 따라 달라질 수 있습니다. 아래 14개 버전은 개발 PC에서 관찰한 환경일 뿐 고객 ZIP의 고정 의존성 집합이 아닙니다.

## 개발 PC 관찰값

| 배포판 | 버전 | 설치 METADATA의 라이선스 필드 | 라이선스 파일 지문 | 판정 |
| --- | --- | --- | --- | --- |
| annotated-doc | 0.0.5 | MIT | `annotated_doc-0.0.5.dist-info/licenses/LICENSE` SHA-256 `fff170779a6acbf65abdb405c087f1cee1786691e4a96a4034517e4a504a0cdf` | UNKNOWN / NOT_GRANTED |
| annotated-types | 0.8.0 | MIT | `annotated_types-0.8.0.dist-info/licenses/LICENSE` SHA-256 `fe1049884b1a0d9342901e88e07f32925d24b3121d9972b6a6805fb9824b095d` | UNKNOWN / NOT_GRANTED |
| anyio | 4.14.2 | MIT | `anyio-4.14.2.dist-info/licenses/LICENSE` SHA-256 `5361ac9dc58f2ef5fd2e9b09c68297c17f04950909bbc8023bdb82eacf22c2b0` | UNKNOWN / NOT_GRANTED |
| click | 8.5.0 | BSD-3-Clause | `click-8.5.0.dist-info/licenses/LICENSE.txt` SHA-256 `9a8ad106a394e853bfe21f42f4e72d592819a22805d991b5f3275029292b658d` | UNKNOWN / NOT_GRANTED |
| fastapi | 0.143.3 | MIT | `fastapi-0.143.3.dist-info/licenses/LICENSE` SHA-256 `4ec89ffc81485b97fec584b2d4a961032eeffe834453894fd9c1274906cc744e` | UNKNOWN / NOT_GRANTED |
| h11 | 0.16.0 | MIT | `h11-0.16.0.dist-info/licenses/LICENSE.txt` SHA-256 `37db5bb85926db28a427a25867f10b1232003aea1be69ccb851138adb8e6f361` | UNKNOWN / NOT_GRANTED |
| idna | 3.19 | BSD-3-Clause | `idna-3.19.dist-info/licenses/LICENSE.md` SHA-256 `1a9a4f0e3d479a27240ddd59a9137a66ab4a0f9dfdc8ca6188cc0bfd85187f04` | UNKNOWN / NOT_GRANTED |
| opentelemetry-api | 1.45.1 | Apache-2.0 | `opentelemetry_api-1.45.1.dist-info/licenses/LICENSE` SHA-256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | UNKNOWN / NOT_GRANTED |
| pydantic | 2.13.5 | MIT | `pydantic-2.13.5.dist-info/licenses/LICENSE` SHA-256 `a9e186f3ca16b5eef84318e7a701721351a00cb7b8ae3a4394b67b49e3529ef3` | UNKNOWN / NOT_GRANTED |
| pydantic-core | 2.46.5 | MIT | `pydantic_core-2.46.5.dist-info/licenses/LICENSE` SHA-256 `fbe7f615f18d135c07000e5a86325db27f42c7729699ef166ac1f7a3f4586bf4` | UNKNOWN / NOT_GRANTED |
| starlette | 1.8.0 | BSD-3-Clause | `starlette-1.8.0.dist-info/licenses/LICENSE.md` SHA-256 `dcb95677a02240243187e964f941847d19b17821cf99e5afae684fab328c19bf` | UNKNOWN / NOT_GRANTED |
| typing-extensions | 4.16.0 | PSF-2.0 | `typing_extensions-4.16.0.dist-info/licenses/LICENSE` SHA-256 `3b2f81fe21d181c499c59a256c8e1968455d6689d269aa85373bfb6af41da3bf` | UNKNOWN / NOT_GRANTED |
| typing-inspection | 0.4.4 | MIT | `typing_inspection-0.4.4.dist-info/licenses/LICENSE` SHA-256 `804b59b25f2c31bd278f9202a19ae49a3945aa2664387e2d0a128c7cacc61ec3` | UNKNOWN / NOT_GRANTED |
| uvicorn | 0.54.0 | BSD-3-Clause | `uvicorn-0.54.0.dist-info/licenses/LICENSE.md` SHA-256 `efe1acf3e62fb99c288b0ec73e5a773b7268ef4320fe757ea994214e4b63c371` | UNKNOWN / NOT_GRANTED |

## 미확인 항목 및 출시 차단 게이트

- 도구는 직접 요구사항 `fastapi>=0.110,<1`, `uvicorn>=0.27,<1`만 선언합니다. 고객 실행 시 resolve되는 버전을 고정하지 않았고, 전체 transitive/extras 집합을 완전히 확장하지 않았습니다.
- wheel 다운로드 및 wheel 해시 검증은 수행하지 않았습니다. 기록된 METADATA/라이선스 파일 지문은 배포 wheel과의 동일성을 입증하지 않습니다.
- 취약점·법률 준수 감사는 수행되지 않았습니다. 패키지 저장소/프로젝트의 정확한 고지 의무와 라이선스 사본 제공 조건도 판정하지 않았습니다.
- REA_Web 원본/파생 코드, 선택적 Fable/Astra 구성 요소, 각 배포판의 재배포·고지 의무, 고객에게 전달되는 런타임 설치 방식은 계약에 쓰기 전에 사람이 검토해야 합니다.
- 담당자가 각 실제 배포 버전 및 파일 지문을 고정한 뒤 라이선스 본문·NOTICE를 공식 배포물에서 검토하고, 필요한 고지를 납품 ZIP에 포함하고, 승인 기록을 남기기 전까지 판매/상용 배포를 승인하지 않습니다.

## 증거 출처

- 기계 수집 원본: `dependency_metadata_2026-10-30.json` (network calls 0).
- 개발자 안내: `dependency_metadata_README.md`.
- 프로젝트 생성기에서 출력하는 현재 런타임 범위: 보존된 원본 스냅샷 `rea/mvp.py`와 `rea/delivery.py`.


## Windows startup recovery check (2026-10-30)

- The generated app performs a loopback-only selected-port probe before Uvicorn launch. The actual Windows CMD occupied-port case returned exit code 2 with stable `REA_LOCAL_PORT_UNAVAILABLE`, Korean instructions to choose another port, and a visible pause. The probe does not reserve the port, so a race can still occur before Uvicorn binds.
- Focused automated customer-guidance tests: **9 passed**.
- Fresh free-port HTTP startup after this launcher change is **NOT_CONFIRMED**: this Windows sandbox did not return the synthetic API rows during the attempt. Prior HTTP evidence refers to the earlier code delta and is not carried forward as proof.
- Fresh delivery ZIP generation reached manifest validation after a test-harness-only `os.replace` substitute for the Windows-sandbox-denied hard-link publish. Actual `os.link` publishing remains unverified in this sandbox; ZIP content validation is not a legal or commercial clearance.

