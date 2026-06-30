@echo off
REM Manual trigger for PVT L2 Report

setlocal enabledelayedexpansion

cd /d "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"

set "PYTHON_EXE=%~dp0..\.venv\Scripts\python.exe"

echo.
echo ========================================
echo  L2 PVT Report - Manual Trigger
echo ========================================
echo.
echo This will generate and send the PVT L2 Report.
echo.
echo 1) Send PVT Report (actual email)
echo 2) Dry Run only (no email sent)
echo 0) Exit
echo.

set /p choice="Enter choice (0-2): "

if "%choice%"=="0" (
    echo Exiting...
    exit /b 0
)

if "%choice%"=="1" (
    echo.
    echo Sending PVT Report...
    if exist "%PYTHON_EXE%" (
        "%PYTHON_EXE%" "%~dp0send_l2_report_outlook_account.py" --report-type pvt
    ) else (
        python "%~dp0send_l2_report_outlook_account.py" --report-type pvt
    )
    echo.
    echo PVT Report sent.
    pause
    exit /b 0
)

if "%choice%"=="2" (
    echo.
    echo Dry Run - generating report only, no email will be sent...
    if exist "%PYTHON_EXE%" (
        "%PYTHON_EXE%" "%~dp0send_l2_report_outlook_account.py" --report-type pvt --dry-run
    ) else (
        python "%~dp0send_l2_report_outlook_account.py" --report-type pvt --dry-run
    )
    echo.
    echo Dry run complete. Check Box folder for generated HTML.
    pause
    exit /b 0
)

echo Invalid choice. Exiting.
pause
