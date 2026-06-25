@echo off
REM Run PowerShell script with admin privileges to update Task Scheduler

echo Requesting Administrator privileges...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb runas -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',\"$PSScriptRoot\fix_task_scheduler.ps1\" -Wait"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo Task scheduler setup completed successfully!
    echo ============================================
    echo.
    echo Your task is scheduled to run daily (Mon-Fri)
    echo Time is set from SCHEDULER_HOUR and SCHEDULER_MINUTE in .env file
    echo Edit .env and run this script again to change the schedule time.
    echo.
) else (
    echo.
    echo ============================================
    echo ERROR: Setup failed!
    echo ============================================
    echo Please run this file as Administrator:
    echo 1. Right-click this file
    echo 2. Select "Run as administrator"
    echo.
)

pause

