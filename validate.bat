@echo off
setlocal EnableDelayedExpansion

set REPO=%~dp0
set DEFAULT_PYTHON_EXE=%REPO%.venv\Scripts\python.exe

if exist "%REPO%config.env" (
    for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%REPO%config.env") do (
        if not "%%A"=="" set %%A=%%B
    )
)

if not defined PYTHON_EXE (
    if exist "%DEFAULT_PYTHON_EXE%" (
        set PYTHON_EXE=%DEFAULT_PYTHON_EXE%
    ) else (
        echo  [ERROR] config.env not found and .venv Python not found. Run install.bat first.
        exit /b 1
    )
)

if not exist "!PYTHON_EXE!" (
    if exist "%DEFAULT_PYTHON_EXE%" (
        echo  [WARN] Python executable from config.env was not found: !PYTHON_EXE!
        echo         Falling back to "%DEFAULT_PYTHON_EXE%".
        set PYTHON_EXE=%DEFAULT_PYTHON_EXE%
    ) else (
        echo  [ERROR] Python executable not found: !PYTHON_EXE!
        exit /b 1
    )
)

if not defined OMNI_KIT_ACCEPT_EULA set OMNI_KIT_ACCEPT_EULA=yes

"!PYTHON_EXE!" "%REPO%setup\validate_env.py" %*
set RC=%ERRORLEVEL%

if "%RC%"=="0" (
    echo  [OK] Environment ready.
) else (
    echo  [FAIL] Environment not ready. See output above. ^(exit %RC%^)
)

endlocal
exit /b %RC%
