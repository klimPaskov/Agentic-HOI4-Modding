@echo off
setlocal
where py >nul 2>nul
if errorlevel 1 (
    echo Python 3.10 or newer and the Windows Python launcher are required.
    pause
    exit /b 1
)
py -3 "%~dp0package_chatgpt_project_sources.py" --open %*
set "package_exit_code=%errorlevel%"
pause
exit /b %package_exit_code%
