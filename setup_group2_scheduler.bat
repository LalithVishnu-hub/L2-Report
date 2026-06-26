@echo off
REM Setup Task Scheduler for L2 Report Group 2
REM This script configures the scheduler to send Group 2 emails on weekdays at 8:30 AM

echo.
echo ========================================
echo L2 Report - Task Scheduler Setup
echo Group 2 (Secondary Contacts)
echo ========================================
echo.
echo NOTE: This script must be run as Administrator!
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges!
    echo Please right-click this file and select "Run as Administrator"
    pause
    exit /b 1
)

REM Run PowerShell script with proper execution policy
cd /d "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"

powershell -NoProfile -ExecutionPolicy Bypass -File ".\setup_task_scheduler_group2.ps1"

pause
