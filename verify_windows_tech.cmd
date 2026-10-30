@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
echo [REA] Four synthetic packages: ZIP build / audited restore / HTTP / Windows CMD.
echo [REA] This is NOT real customer acceptance or commercial clearance.
call python -c "import sys;sys.exit(0 if sys.version_info[:2]>=(3,11) else 1)" >nul 2>nul
if not errorlevel 1 goto use_python
call py -3 -c "import sys;sys.exit(0 if sys.version_info[:2]>=(3,11) else 1)" >nul 2>nul
if not errorlevel 1 goto use_py
echo [REA] ERROR: Python 3.11+ is required. Nothing was installed.
set "REA_QA_EXIT=10"
goto done
:use_python
call python -m scripts.rea_final_technical_smoke --native
set "REA_QA_EXIT=%ERRORLEVEL%"
goto done
:use_py
call py -3 -m scripts.rea_final_technical_smoke --native
set "REA_QA_EXIT=%ERRORLEVEL%"
:done
if "%REA_QA_EXIT%"=="0" (
  echo [REA] PASS_SYNTHETIC_TECHNICAL_ONLY. Human and commercial gates remain OPEN.
) else (
  echo [REA] FAIL_OR_NOT_RUN: exit %REA_QA_EXIT%. Review error output above.
  echo [REA] Missing packages may require a user-approved dependency install.
)
echo [REA] Capture the exit status without sharing any private CSV or SQLite.
pause
exit /b %REA_QA_EXIT%
