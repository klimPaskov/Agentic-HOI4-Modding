@echo off
setlocal

if not defined MESHY_API_KEY goto missing_meshy_key

set "PIPELINE_ROOT=%~dp0.."
set "VERSION_FILE=%PIPELINE_ROOT%\config\meshy_mcp_version.txt"
set "NPX_RECORD=%PIPELINE_ROOT%\config\npx_executable.txt"

if not exist "%VERSION_FILE%" (
  echo The bootstrap did not record the resolved latest Meshy MCP version.
  exit /b 3
)
set /p MESHY_MCP_VERSION=<"%VERSION_FILE%"
if "%MESHY_MCP_VERSION%"=="" (
  echo The bootstrap recorded an empty Meshy MCP version.
  exit /b 3
)
if not exist "%NPX_RECORD%" goto missing_npx
set /p NPX_EXE=<"%NPX_RECORD%"
if not exist "%NPX_EXE%" goto missing_npx

call "%NPX_EXE%" --yes @meshy-ai/meshy-mcp-server@%MESHY_MCP_VERSION%
exit /b %errorlevel%

:missing_npx
echo The reviewed npx.cmd path is missing. Run the 3D bootstrap again.
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
