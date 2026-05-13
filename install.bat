@echo off
setlocal EnableDelayedExpansion

set REPO=%~dp0
set VENV=%REPO%.venv

echo.
echo  ============================================================
echo   usd-convert-cad - Setup
echo  ============================================================
echo.

set PY312=
where py >nul 2>&1
if not errorlevel 1 (
    py -3.12 --version >nul 2>&1
    if not errorlevel 1 set PY312=py -3.12
)

if not defined PY312 (
    where python >nul 2>&1
    if errorlevel 1 (
        echo  [ERROR] Python was not found. Install Python 3.12 and rerun.
        exit /b 1
    )
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
    for /f "tokens=1,2 delims=." %%a in ("!PY_VER!") do (
        set PY_MAJOR=%%a
        set PY_MINOR=%%b
    )
    if "!PY_MAJOR!"=="3" if "!PY_MINOR!"=="12" set PY312=python
)

if not defined PY312 (
    echo  [ERROR] Python 3.12 is required for omniverse-kit Windows wheels.
    echo          Install Python 3.12 or make py -3.12 available.
    exit /b 1
)

echo  [OK] Using Python: !PY312!

if not exist "%VENV%\Scripts\python.exe" (
    echo  Creating virtual environment...
    !PY312! -m venv "%VENV%"
    if errorlevel 1 exit /b 1
)

set VENV_PY=%VENV%\Scripts\python.exe

echo  Upgrading pip...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

echo  Installing omniverse-kit from NVIDIA PyPI...
"%VENV_PY%" -m pip install -r "%REPO%requirements.txt" --extra-index-url https://pypi.nvidia.com
if errorlevel 1 exit /b 1

echo  Installing repo package in editable mode...
"%VENV_PY%" -m pip install -e "%REPO:~0,-1%" --no-deps
if errorlevel 1 exit /b 1

set CFG=%REPO%config.env
echo # usd-convert-cad configuration> "%CFG%"
echo PYTHON_EXE=%VENV_PY%>> "%CFG%"
echo OMNI_KIT_ACCEPT_EULA=yes>> "%CFG%"

echo  Pre-fetching converter extensions from the Kit registry...
"%VENV_PY%" "%REPO%setup\fetch_extensions.py"
if errorlevel 1 (
    echo  [WARN] Extension prefetch did not fully complete. Conversion will retry on first run.
)

echo.
echo  Setup complete.
echo  Run validate.bat to verify the environment.
echo.

endlocal
exit /b 0
