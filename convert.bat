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

if "%~1"=="--formats" (
    "!PYTHON_EXE!" "%REPO%app\run_conversion.py" --formats
    exit /b %ERRORLEVEL%
)

if "%~1"=="" (
    echo.
    echo  Usage: convert.bat ^<input_file^> [output_file] [options]
    echo.
    echo  Examples:
    echo    convert.bat model.jt out\model.usd
    echo    convert.bat model.jt out\model.usd --backend jt_core
    echo    convert.bat model.jt out\model.usd --backend auto --report out\_conversion\model.json --quiet
    echo    convert.bat site.dgn out\site.usd --backend dgn_core
    echo    convert.bat --formats
    echo.
    exit /b 1
)

set INPUT_FILE=%~1
set OUTPUT_ARG=
set QUIET=0
set LOG_FILE=
set REPORT_PATH=
set RC=0
shift

if not "%~1"=="" (
    set SECOND=%~1
    if not "!SECOND:~0,2!"=="--" (
        set OUTPUT_ARG=--output "%~1"
        shift
    )
)

set PASSTHROUGH=
:collect
if "%~1"=="" goto :run
if /I "%~1"=="--quiet" goto :collect_quiet
if /I "%~1"=="--log" goto :collect_log
if /I "%~1"=="--report" goto :collect_report
set PASSTHROUGH=!PASSTHROUGH! "%~1"
shift
goto :collect

:collect_quiet
set QUIET=1
shift
goto :collect

:collect_log
shift
if "%~1"=="" goto :missing_log
set LOG_FILE=%~1
shift
goto :collect

:collect_report
set PASSTHROUGH=!PASSTHROUGH! "%~1"
shift
if "%~1"=="" goto :missing_report
set REPORT_PATH=%~1
set PASSTHROUGH=!PASSTHROUGH! "%~1"
shift
goto :collect

:missing_log
echo  [ERROR] --log requires a file path.
goto :fail

:missing_report
echo  [ERROR] --report requires a file path.
goto :fail

:run
if "%QUIET%"=="1" (
    if not defined REPORT_PATH (
        echo  [ERROR] --quiet requires an explicit --report path.
        goto :fail
    )
    if not defined LOG_FILE (
        for %%F in ("!REPORT_PATH!") do set LOG_FILE=%%~dpnF.log
    )
    for %%F in ("!LOG_FILE!") do if not exist "%%~dpF" mkdir "%%~dpF"
    "!PYTHON_EXE!" "%REPO%app\run_conversion.py" --input "%INPUT_FILE%" !OUTPUT_ARG! !PASSTHROUGH! > "!LOG_FILE!" 2>&1
    set RC=!ERRORLEVEL!
    if exist "!REPORT_PATH!" (
        "!PYTHON_EXE!" -c "import json,sys; sys.exit(0 if json.load(open(sys.argv[1], encoding='utf-8')).get('passed') else 1)" "!REPORT_PATH!" > nul 2>&1
        set RC=!ERRORLEVEL!
    )
    if "!RC!"=="0" (
        echo  [OK] Conversion completed.
        echo  Report: !REPORT_PATH!
        echo  Log: !LOG_FILE!
    ) else (
        echo  [FAIL] Conversion failed.
        echo  Report: !REPORT_PATH!
        echo  Log: !LOG_FILE!
    )
) else (
    "!PYTHON_EXE!" "%REPO%app\run_conversion.py" --input "%INPUT_FILE%" !OUTPUT_ARG! !PASSTHROUGH!
    set RC=!ERRORLEVEL!
)

:finish
endlocal & exit /b %RC%

:fail
endlocal & exit /b 1
