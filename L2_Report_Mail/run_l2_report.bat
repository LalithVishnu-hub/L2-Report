@echo off
REM L2 Report Task Scheduler Wrapper
REM This batch file runs the L2 report and sends email via Outlook
REM Now located in L2_Report_Mail folder

cd /d "%~dp0"

REM Run Python script (now in same folder)
python send_l2_report_outlook_account.py

REM Exit with success
exit /b 0
