@echo off
REM L2 Report Task Scheduler Wrapper
REM Generates report, sends email via Outlook, then pushes HTML pages to GitHub Pages

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0..\.venv\Scripts\python.exe"
set "PROJECT_ROOT=%~dp0.."

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" "%~dp0send_l2_report_outlook_account.py"
    set SEND_RESULT=%ERRORLEVEL%
) else (
    python "%~dp0send_l2_report_outlook_account.py"
    set SEND_RESULT=%ERRORLEVEL%
)

REM Push generated html_reports to GitHub so GitHub Pages stays updated
echo.
echo Pushing HTML reports to GitHub...
cd /d "%PROJECT_ROOT%"
git add html_reports/
git commit -m "Auto: L2 report + L1 static pages [%DATE% %TIME%]" --allow-empty
git push origin HEAD
if %ERRORLEVEL% EQU 0 (
    echo [OK] GitHub Pages updated successfully.
) else (
    echo [WARN] Git push failed - check internet connection or token in .env
)

exit /b %SEND_RESULT%
