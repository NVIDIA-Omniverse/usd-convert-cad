@echo off
setlocal EnableDelayedExpansion

set REPO=%~dp0

if not exist "%REPO%config.env" (
    echo  [ERROR] config.env not found. Run install.bat first.
    exit /b 1
)

for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%REPO%config.env") do (
    if not "%%A"=="" set %%A=%%B
)

if not defined PYTHON_EXE (
    echo  [ERROR] PYTHON_EXE not set in config.env. Re-run install.bat.
    exit /b 1
)

if not exist "!PYTHON_EXE!" (
    echo  [ERROR] Python executable not found: !PYTHON_EXE!
    exit /b 1
)

if not defined OMNI_KIT_ACCEPT_EULA set OMNI_KIT_ACCEPT_EULA=yes

"!PYTHON_EXE!" "%REPO%setup\validate_env.py" %*
set RC=%ERRORLEVEL%

endlocal
exit /b %RC%
