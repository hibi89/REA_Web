"""Customer-readable prerequisite guidance without touching app files."""
from __future__ import annotations

from rea.customer_self_check import _version_meets_minimum, render_customer_report
from rea.delivery import CHECK_LAUNCH, DELIVERY_ACCEPTANCE, LAUNCH, WINDOWS_README


def result(**changes):
    value = {
        "status": "FAIL_LOCAL_PREREQUISITES",
        "python_311_or_later": True,
        "integrity": "NOT_VERIFIED",
        "database": "NOT_CHECKED",
        "dependencies": [],
        "issues": ["Archive/extraction/SQLite validation failed: ValueError"],
    }
    value.update(changes)
    return value


def test_dependency_security_floor_rejects_affected_starlette_versions():
    assert _version_meets_minimum("1.3.1", (1, 3, 1))
    assert _version_meets_minimum("1.3.1.post1", (1, 3, 1))
    assert _version_meets_minimum("1.8.0", (1, 3, 1))
    assert not _version_meets_minimum("1.3.0", (1, 3, 1))
    assert not _version_meets_minimum("1.3.1rc1", (1, 3, 1))
    assert not _version_meets_minimum("0.99.0", (1, 3, 1))


def test_outdated_dependency_has_customer_recovery_guidance():
    report = render_customer_report(result(
        dependencies=[{
            "name": "starlette", "version": "1.0.0",
            "minimum_version": "1.3.1", "status": "VERSION_BELOW_MINIMUM",
        }],
        issues=["Python dependency below minimum: starlette 1.0.0; required >= 1.3.1"],
    ))
    assert "VERSION_BELOW_MINIMUM" in report
    assert "starlette 1.0.0" in report
    assert "필요 >= 1.3.1" in report
    assert "업그레이드 명령" in report


def test_integrity_failure_explains_clean_recovery_and_no_launch():
    report = render_customer_report(result())
    assert "새 폴더" in report
    assert "직접 편집하거나 추가하지 마세요" in report
    assert "launch_windows.cmd를 실행하지 마세요" in report
    assert "고객 파일을 업로드하거나 자동 수정하지 않습니다" in report


def test_missing_python_and_packages_point_to_customer_guide():
    report = render_customer_report(result(
        python_311_or_later=False,
        integrity="MATCHED_DELIVERY_MANIFEST_SHA256",
        database="READONLY_OPEN_SUCCESS",
        dependencies=[{"name": "uvicorn", "status": "MISSING_INSTALL_REQUIRED"}],
        issues=["Missing Python dependency: uvicorn"],
    ))
    assert "Python 3.11 이상" in report
    assert "MISSING_INSTALL_REQUIRED" in report
    assert "uvicorn" in report
    assert "README_WINDOWS.md" in report


def test_success_report_does_not_claim_commercial_or_human_acceptance():
    report = render_customer_report(result(
        status="PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE",
        python_311_or_later=True,
        integrity="MATCHED_DELIVERY_MANIFEST_SHA256",
        database="READONLY_OPEN_SUCCESS",
        dependencies=[{"name": "fastapi", "status": "INSTALLED_UNVERIFIED_LICENSE"}],
        issues=[],
    ))
    assert "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE" in report
    assert "사람의 고객 검수나 상용 권리 승인을 뜻하지 않습니다" in report
    assert "human_acceptance=NOT_RUN" in report
    assert "commercial_clearance=NOT_GRANTED" in report


def test_delivery_acceptance_checklist_covers_core_customer_flow():
    assert "검색 결과" in DELIVERY_ACCEPTANCE
    assert "카테고리 필터" in DELIVERY_ACCEPTANCE
    assert "상세 내용을 확인" in DELIVERY_ACCEPTANCE
    assert "Ctrl+C" in DELIVERY_ACCEPTANCE
    assert "ROW APPEND" in DELIVERY_ACCEPTANCE
    assert "실제 CSV" in DELIVERY_ACCEPTANCE


def test_generated_windows_assets_are_included_and_keep_safe_interpreter_routes():
    checker = CHECK_LAUNCH.encode("ascii")
    launcher = LAUNCH.encode("ascii")
    assert b"chcp 65001 >nul" in checker and b"chcp 65001 >nul" in launcher
    assert b'set "PYTHONIOENCODING=utf-8"' in checker + launcher
    assert b'call python "%~dp0self_check.py" --customer-check' in checker
    assert b'call py -3 "%~dp0self_check.py" --customer-check' in checker
    assert "%REA_WEB_PORT%" not in CHECK_LAUNCH + LAUNCH
    assert "ACCEPTANCE_CHECKLIST.md" in WINDOWS_README
    assert "검사 폴더 밖" in WINDOWS_README
    assert "원본 ZIP" in WINDOWS_README
    assert "ROW APPEND" in DELIVERY_ACCEPTANCE
    assert "REA_LOCAL_PORT_UNAVAILABLE" in WINDOWS_README
    assert "pause" in LAUNCH.lower()
    assert "Follow the recovery steps shown above." in LAUNCH


def test_port_error_message_is_customer_actionable(monkeypatch, capsys):
    from rea import customer_self_check

    monkeypatch.setattr(customer_self_check, "inspect", lambda root: {
        "status": "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE",
        "python_311_or_later": True,
        "integrity": "MATCHED_DELIVERY_MANIFEST_SHA256",
        "database": "READONLY_OPEN_SUCCESS",
        "dependencies": [],
        "issues": [],
    })
    monkeypatch.setenv("REA_WEB_PORT", "8000&echo BAD")
    assert customer_self_check.launch_local(".") == 2
    report = capsys.readouterr().err
    assert "포트 번호는 1~65535 숫자만" in report
    assert "set REA_WEB_PORT=8765" in report
    assert "BAD" not in report


def test_windows_readme_discloses_unencrypted_customer_database():
    assert "암호화되지 않았으며" in WINDOWS_README
    assert "app\\data.sqlite" in WINDOWS_README
    assert "개인/민감정보" in WINDOWS_README

def test_customer_cli_mode_is_plain_text_and_preserves_exit_code(monkeypatch, capsys):
    from rea import customer_self_check

    monkeypatch.setattr(customer_self_check, "inspect", lambda root: result())
    assert customer_self_check.main(["--root", ".", "--customer-check"]) == 2
    output = capsys.readouterr().out
    assert output.startswith("REA_Web 납품 앱 사전 검사")
    assert output.count("FAIL_LOCAL_PREREQUISITES") == 1


def test_default_cli_keeps_json_contract(monkeypatch, capsys):
    import json
    from rea import customer_self_check

    monkeypatch.setattr(customer_self_check, "inspect", lambda root: result())
    assert customer_self_check.main(["--root", "."]) == 2
    document = json.loads(capsys.readouterr().out)
    assert document["status"] == "FAIL_LOCAL_PREREQUISITES"


def test_occupied_port_is_reported_before_server_launch(monkeypatch, capsys):
    import socket
    from rea import customer_self_check

    monkeypatch.setattr(customer_self_check, "inspect", lambda root: {
        "status": "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE",
        "python_311_or_later": True,
        "integrity": "MATCHED_DELIVERY_MANIFEST_SHA256",
        "database": "READONLY_OPEN_SUCCESS",
        "dependencies": [],
        "issues": [],
    })
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as occupied:
        occupied.bind(("127.0.0.1", 0))
        occupied.listen(1)
        monkeypatch.setenv("REA_WEB_PORT", str(occupied.getsockname()[1]))
        monkeypatch.setattr(customer_self_check.subprocess, "run",
                            lambda *args, **kwargs: pytest.fail("must not launch on occupied port"))
        assert customer_self_check.launch_local(".") == 2
    report = capsys.readouterr().err
    assert "REA_LOCAL_PORT_UNAVAILABLE" in report
    assert "set REA_WEB_PORT=8765" in report

