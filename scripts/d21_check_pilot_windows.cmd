@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem Synthetic pilot kit verifier ONLY. Python 3.11+ needed; no install/network/app start.
rem Use --check in scripts to skip the double-click result pause.
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
if not "%~2"=="" goto invalid
if "%~1"=="" goto select
if /I "%~1"=="--check" goto select
goto invalid

:select
if not exist "%~dp0CHECK_PILOT_OFFLINE.py" goto missing_checker
where py >nul 2>nul
if errorlevel 1 goto python_fallback
py -3.11 -c "import sys;sys.exit(0 if sys.version_info[:2]>=(3,11) else 1)" >nul 2>nul
if errorlevel 1 goto python_fallback
py -3.11 "%~dp0CHECK_PILOT_OFFLINE.py"
set "_rea_result=%ERRORLEVEL%"
goto finished

:python_fallback
where python >nul 2>nul
if errorlevel 1 goto no_python
python -c "import sys;sys.exit(0 if sys.version_info[:2]>=(3,11) else 1)" >nul 2>nul
if errorlevel 1 goto no_python
python "%~dp0CHECK_PILOT_OFFLINE.py"
set "_rea_result=%ERRORLEVEL%"
goto finished

:no_python
echo [REA] MISSING_PYTHON: Python 3.11+ is needed. Nothing was installed.
set "_rea_result=10"
goto finished

:missing_checker
echo [REA] MISSING_CHECKER: Cannot locate CHECK_PILOT_OFFLINE.py beside this launcher.
set "_rea_result=11"
goto finished

:invalid
echo [REA] INVALID_ARGUMENT: Double-click without arguments or run --check.
exit /b 2

:finished
if not "%_rea_result%"=="0" echo [REA] KIT_NOT_VERIFIED. Do not launch the demo.
if "%~1"=="" (
  echo [REA] Read the result above. This is NOT human or commercial acceptance.
  pause
)
exit /b %_rea_result%
