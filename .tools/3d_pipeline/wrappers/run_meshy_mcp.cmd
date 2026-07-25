@echo off
setlocal

if "%MESHY_API_KEY:~0,1%"=="" goto missing_meshy_key

set "PIPELINE_ROOT=%~dp0.."
set "BOOTSTRAP=%PIPELINE_ROOT%\bootstrap_3d_workflow.py"
set "VERSION_FILE=%PIPELINE_ROOT%\config\meshy_mcp_version.txt"
set "PYTHON_EXE=python"
where python >nul 2>nul
if errorlevel 1 set "PYTHON_EXE=py -3"
%PYTHON_EXE% "%BOOTSTRAP%" --quiet
if errorlevel 1 exit /b %errorlevel%

if not exist "%VERSION_FILE%" (
  echo The bootstrap did not record the resolved latest Meshy MCP version.
  exit /b 3
)
set /p MESHY_MCP_VERSION=<"%VERSION_FILE%"
if "%MESHY_MCP_VERSION%"=="" (
  echo The bootstrap recorded an empty Meshy MCP version.
  exit /b 3
)
set "NPX_EXE="
for /f "delims=" %%N in ('where npx.cmd 2^>nul') do if not defined NPX_EXE set "NPX_EXE=%%N"
if not defined NPX_EXE goto missing_npx

call "%NPX_EXE%" --yes @meshy-ai/meshy-mcp-server@%MESHY_MCP_VERSION%
exit /b %errorlevel%

:missing_npx
echo npx.cmd is required for the resolved latest Meshy MCP route.
exit /b 3

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
