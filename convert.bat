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
    echo    convert.bat site.dgn out\site.usd --backend dgn_core
    echo    convert.bat --formats
    echo.
    exit /b 1
)

set INPUT_FILE=%~1
set OUTPUT_ARG=
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
set PASSTHROUGH=!PASSTHROUGH! %1
shift
goto :collect

:run
"!PYTHON_EXE!" "%REPO%app\run_conversion.py" --input "%INPUT_FILE%" !OUTPUT_ARG! !PASSTHROUGH!
set RC=%ERRORLEVEL%

endlocal
exit /b %RC%
