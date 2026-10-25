@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem REA_Web local offline creator entrypoint. No downloads, pip, admin, registry or PATH changes.
cd /d "%~dp0"
if errorlevel 1 (
  echo [REA] Cannot access the local project directory.
  exit /b 13
)

set "_rea_python="
set "_rea_switch="
if exist "%~dp0.venv\Scripts\python.exe" (
  set "_rea_python=%~dp0.venv\Scripts\python.exe"
  goto selected
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3.11 -c "import sys;sys.exit(0 if sys.version_info[:2]>=(3,11) else 1)" >nul 2>nul
  if not errorlevel 1 (
    set "_rea_python=py"
    set "_rea_switch=-3.11"
    goto selected
  )
)
where python >nul 2>nul
if not errorlevel 1 (
  set "_rea_python=python"
  goto selected
)
echo [REA] NO_PYTHON: Python 3.11+ is required. No software was installed.
exit /b 10

:selected
if "%~1"=="" goto launch
if /I "%~1"=="--check" goto check
echo [REA] INVALID_ARGUMENT: double click to open, or run --check.
exit /b 2

:check
"%_rea_python%" %_rea_switch% -m rea.creator_preflight --check
exit /b %ERRORLEVEL%

:launch
"%_rea_python%" %_rea_switch% -m rea.creator_preflight --launch
set "_rea_exit=%ERRORLEVEL%"
if not "%_rea_exit%"=="0" (
  echo [REA] GUI not started. See the diagnostic above. No package was installed.
  pause
)
exit /b %_rea_exit%
