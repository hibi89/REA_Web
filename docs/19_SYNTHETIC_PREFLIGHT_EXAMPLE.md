# REA_WEB — v0.2 합성 JSON 응답 검증 예제

**상태: SELF-AUTHORED SYNTHETIC ONLY / REVIEW REQUIRED / RELEASE HOLD**

이 문서는 자체 제작한 가짜 작업 목록·지표·상세 응답으로 재현할 수 있는 오프라인 계약 검증 절차입니다. 고객 ZIP/API, 고객 인증정보, 실제 운영 데이터, Fable 원격 스크래핑, Docker, 웹 배포를 사용하지 않습니다. 예제 Fable의 https://example.org/ 는 설명용 URL 문자열일 뿐 실제 접속하지 않습니다.

## 구조와 안전 경계

1. rea.adapter.synthetic_example 가 고정된 자체 제작 Fable/Backend 정적 힌트와 명시된 필드 매핑을 frontend_bridge.make_review()로 검토합니다.
2. review.json 을 결정적인 UTF-8 JSON 바이트로 작성하고 SHA-256을 계산합니다.
3. synthetic_samples.json 에 같은 SHA, 리뷰 스키마 버전, 가짜 백엔드 SHA, 합성 list/metrics/detail GET 200 JSON 응답 문자열을 기록합니다. 샘플 스키마는 rea.synthetic_response_samples.v0.2 입니다.
4. rea.adapter.response_preflight 가 SHA/스키마/백엔드 일치, 목록/지표/상세 일관성, 크기/필드/인증정보 차단 규칙을 검사합니다.
5. 성공해도 SYNTHETIC_PREFLIGHT_REVIEW_REQUIRED 이며 generation_allowed, release_allowed, customer_runtime_verified, source_rights_verified 는 모두 false 입니다. SHA는 우발적인 파일 뒤바뀜 감지일 뿐 서명·법적 권리·실제 API 증거가 아닙니다.

두 예제 파일의 생성은 기존 디렉터리를 덮어쓰지 않는 원자적 출판을 사용합니다. 이미 존재하는 대상 디렉터리, 부모 디렉터리가 없는 대상, 심볼릭 링크 대상은 거부합니다. 보고서는 새 파일에만 기록합니다.

## Windows PowerShell — 실제 재현 명령

저장소 최상위에서 실행하며 출력 경로는 아직 없는 새 디렉터리여야 합니다.

~~~powershell
python -m rea.adapter.synthetic_example --out .\rea_v02_example
python -m rea.adapter.response_preflight --review .\rea_v02_example\review.json --samples .\rea_v02_example\synthetic_samples.json --synthetic-only --out .\rea_v02_report.json
~~~

rea_v02_example 또는 rea_v02_report.json 이 이미 있으면 다른 새 이름을 사용하십시오. 기존 파일을 삭제·덮어쓰지 마십시오. 이 검증 자체에는 네트워크가 필요 없습니다.

## Ubuntu/Linux — 실제 재현 명령

~~~bash
python3 -m rea.adapter.synthetic_example --out ./rea_v02_example
python3 -m rea.adapter.response_preflight --review ./rea_v02_example/review.json --samples ./rea_v02_example/synthetic_samples.json --synthetic-only --out ./rea_v02_report.json
~~~

해시만 독립 확인하려면 PowerShell의 (Get-FileHash -Algorithm SHA256 .\rea_v02_example\review.json).Hash.ToLowerInvariant() 또는 Linux의 sha256sum ./rea_v02_example/review.json 을 사용하십시오. synthetic_samples.json 의 review_sha256 과 같아야 합니다. 입력을 다시 직렬화하거나 공백만 변경해도 다른 파일 해시가 되므로 새 합성 샘플을 재생성해야 합니다.

## 합성 응답 예

- GET /api/jobs → items 2개. EXAMPLE-001 은 완료(done), EXAMPLE-002 는 대기(pending) 상태.
- GET /api/metrics → 전체 2, 완료 1, 대기 1.
- GET /api/jobs/{job_id} → 선택된 EXAMPLE-001 의 상세값. 실제 HTTP 요청은 하지 않습니다.
- 응답 본문은 synthetic_samples.json 의 samples.<role>.body 에 JSON 문자열로 직렬화합니다. 실행 코드, 실제 데이터, 토큰, 쿠키는 넣지 않습니다.

정상 검증의 stdout/보고서 핵심 값:

~~~json
{
  "schema_version": "rea.synthetic_response_preflight.v0.2",
  "status": "SYNTHETIC_PREFLIGHT_REVIEW_REQUIRED",
  "review_status": "OWNER_REVIEW_REQUIRED",
  "sample_contract_status": "SYNTHETIC_SHAPES_MATCH_REVIEW_REQUIRED",
  "sample_rows": 2,
  "generation_allowed": false,
  "release_allowed": false,
  "customer_runtime_verified": false,
  "source_rights_verified": false,
  "execution_performed": false,
  "network_performed": false
}
~~~

전체 보고서에는 제한사항과 검사 역할이 추가됩니다. 원본 작업 ID나 원문 응답값은 보고서에 포함하지 않습니다.

## 회귀 검증과 거부 정책

~~~bash
python -m pytest -q tests/test_backend_zip.py tests/test_adapter.py tests/test_rea_lite_integration.py tests/test_response_contract.py tests/test_response_preflight.py tests/test_synthetic_example.py
~~~

tests/test_synthetic_example.py 는 실제 subprocess로 Python 모듈 생성 → 합성 검증 → 보고서 출력을 점검합니다. 결정성, 중복 생성 거부, 기존 빈 디렉터리 보호, 리뷰 바이트 변조, KPI 수량 불일치 및 실행 가능한 앱/백엔드 산출물 미생성을 검사합니다.

해시/버전/자료형/필드 불일치, 인증정보 필드, 기존 출력 경로는 거부됩니다. CLI 종료 코드 0 은 합성 검증 REVIEW REQUIRED, 2 는 거부입니다. 종료 코드 0 을 고객 소프트웨어의 정상성·보안·라이선스·납품 적합성으로 간주해서는 안 됩니다.

## 상용화 전 남은 조건

실제 고객 자료 사용 권리, 실제 API/인증 응답 계약, 실물 Windows 운영자 검증, 소스·의존성 라이선스, 별도 승인된 Docker/VM 격리와 보안, 최종 상품 계약과 출시 승인이 필요합니다. 고객 ZIP 실행·외부 업로드·Production 배포는 별도 사용자 승인 전 금지입니다. 기존 Pro·Lite 원본을 유지합니다.
