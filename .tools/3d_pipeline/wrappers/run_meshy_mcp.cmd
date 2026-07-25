@echo off
setlocal

if "%MESHY_API_KEY:~0,1%"=="" goto missing_meshy_key

set "PIPELINE_ROOT=%~dp0.."
set "BOOTSTRAP=%PIPELINE_ROOT%\bootstrap_3d_workflow.py"
set "RUNTIME_RECORD=%PIPELINE_ROOT%\config\runtime.json"
set "PYTHON_EXE=py -3.13"
if not exist "%RUNTIME_RECORD%" (
  %PYTHON_EXE% "%BOOTSTRAP%" --quiet
  if errorlevel 1 exit /b %errorlevel%
)

if "%MESHY_MCP_VERSION%"=="" set "MESHY_MCP_VERSION=0.4.0"
set "NPX_EXE=C:\Program Files\nodejs\npx.cmd"
if not exist "%NPX_EXE%" for /f "delims=" %%N in ('where npx.cmd 2^>nul') do if not defined NPX_FOUND set "NPX_FOUND=%%N"
if defined NPX_FOUND set "NPX_EXE=%NPX_FOUND%"
if not exist "%NPX_EXE%" goto missing_npx

call "%NPX_EXE%" --yes @meshy-ai/meshy-mcp-server@%MESHY_MCP_VERSION%
exit /b %errorlevel%

:missing_npx
echo npx.cmd is required for the pinned Meshy MCP route.
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
