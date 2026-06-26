@echo off
REM Manual trigger for L2 Report - Choose contact group

setlocal enabledelayedexpansion

cd /d "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"

echo.
echo ========================================
echo L2 Report - Manual Trigger
echo ========================================
echo.
echo Select which contact group to send to:
echo.
echo 1) Group 1 (Primary contacts)
echo 2) Group 2 (Secondary contacts)
echo 3) Both groups
echo 0) Exit
echo.

set /p choice="Enter choice (0-3): "

if "%choice%"=="0" (
    echo Exiting...
    exit /b 0
)

if "%choice%"=="1" (
    echo.
    echo Sending to Group 1...
    python "L2_Report_Mail\send_l2_report_outlook_account.py" --group group1
    echo.
    echo Group 1 email sent.
    pause
    exit /b 0
)

if "%choice%"=="2" (
    echo.
    echo Sending to Group 2...
    python "L2_Report_Mail\send_l2_report_outlook_account.py" --group group2
    echo.
    echo Group 2 email sent.
    pause
    exit /b 0
)

if "%choice%"=="3" (
    echo.
    echo Sending to Group 1...
    python "L2_Report_Mail\send_l2_report_outlook_account.py" --group group1
    timeout /t 5 /nobreak
    echo.
    echo Sending to Group 2...
    python "L2_Report_Mail\send_l2_report_outlook_account.py" --group group2
    echo.
    echo Both groups have been sent.
    pause
    exit /b 0
)

echo Invalid choice. Exiting.
pause
exit /b 1
