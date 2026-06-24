@echo off
REM Schedule L2 Report - Elevated Execution Helper
REM This script will attempt to run the scheduler setup with admin privileges

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%fix_task_scheduler.ps1"

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo Requesting Administrator privileges...
    echo ============================================
    echo.
    
    REM Create a temporary VBScript to run PowerShell with admin
    set "TEMP_VBS=%TEMP%\elevate_ps.vbs"
    
    (
        echo Set UAC = CreateObject("Shell.Application"^)
        echo UAC.ShellExecute "powershell.exe", "-NoProfile -ExecutionPolicy Bypass -File ""!PS_SCRIPT!""", "", "runas", 1
    ) > "!TEMP_VBS!"
    
    cscript.exe "!TEMP_VBS!"
    del "!TEMP_VBS!" 2>nul
    
    timeout /t 3 /nobreak
    goto done
)

REM If we get here, we're already admin - run the script
echo Running scheduler setup with admin privileges...
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

:done
echo.
pause
