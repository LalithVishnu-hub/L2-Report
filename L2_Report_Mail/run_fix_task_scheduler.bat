@echo off
REM Run PowerShell script with admin privileges to update Task Scheduler
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%fix_task_scheduler.ps1"

echo.
echo Requesting Administrator privileges...
echo.

REM Run PowerShell script with elevated privileges
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%"
set PS_EXIT=%ERRORLEVEL%

if %PS_EXIT% EQU 0 (
    echo.
    echo ============================================
    echo [SUCCESS] Task Scheduler setup complete!
    echo ============================================
) else (
    echo.
    echo ============================================
    echo [ERROR] Setup failed - exit code %PS_EXIT%
    echo ============================================
    echo Please run this batch file as Administrator:
    echo 1. Right-click this file
    echo 2. Select "Run as administrator"
    echo.
)

pause
exit /b %PS_EXIT%
