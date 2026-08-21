@echo off
setlocal

if not defined MESHY_API_KEY goto missing_meshy_key

set "VERIFIED_LAUNCHER=%~dp0..\run_verified_meshy.py"
python -I "%VERIFIED_LAUNCHER%"
exit /b %errorlevel%

:missing_meshy_key
echo MESHY_API_KEY is missing. Stop before starting Meshy.
echo Run:
echo [Environment]::SetEnvironmentVariable^(
echo     "MESHY_API_KEY",
echo     "msy_your_actual_key_here",
echo     "User"
echo ^)
echo Then restart the shell or Codex.
exit /b 2
