@echo off
REM Run PowerShell script with admin privileges
REM This schedules the L2 Report to run daily at 12:30 AM

echo Requesting Administrator privileges...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb runas -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',\"$PSScriptRoot\fix_task_scheduler.ps1\" -Wait"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo Task scheduler setup completed successfully!
    echo ============================================
    echo.
    echo Your task is scheduled to run daily at 12:30 AM
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

