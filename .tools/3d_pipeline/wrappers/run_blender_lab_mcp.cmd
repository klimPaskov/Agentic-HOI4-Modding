@echo off
setlocal

if "%MESHY_API_KEY:~0,1%"=="" goto missing_meshy_key

set "PIPELINE_ROOT=%~dp0.."
set "BOOTSTRAP=%PIPELINE_ROOT%\bootstrap_3d_workflow.py"
set "PROJECT_RECORD=%PIPELINE_ROOT%\config\blender_mcp_project.txt"
set "UV_RECORD=%PIPELINE_ROOT%\config\uv_executable.txt"
set "BRIDGE_HOST_RECORD=%PIPELINE_ROOT%\config\blender_mcp_host.txt"
set "BRIDGE_PORT_RECORD=%PIPELINE_ROOT%\config\blender_mcp_port.txt"
set "UV_PROJECT_ENVIRONMENT=%PIPELINE_ROOT%\vendor\blender_mcp_venv"
set "PYTHON_EXE=python"
where python >nul 2>nul
if errorlevel 1 set "PYTHON_EXE=py -3"
%PYTHON_EXE% "%BOOTSTRAP%" --quiet
if errorlevel 1 exit /b %errorlevel%

if not exist "%PROJECT_RECORD%" (
  echo The bootstrap did not record the resolved latest Blender MCP project.
  exit /b 3
)
set /p BLENDER_MCP_PROJECT=<"%PROJECT_RECORD%"
if "%BLENDER_MCP_PROJECT%"=="" (
  echo The bootstrap recorded an empty Blender MCP project.
  exit /b 3
)
if not exist "%BRIDGE_HOST_RECORD%" if not exist "%BRIDGE_PORT_RECORD%" (
  echo The bootstrap did not record the resolved Blender MCP bridge.
  exit /b 3
)
set /p BLENDER_MCP_HOST=<"%BRIDGE_HOST_RECORD%"
set /p BLENDER_MCP_PORT=<"%BRIDGE_PORT_RECORD%"
if "%BLENDER_MCP_HOST%"=="" set "BLENDER_MCP_HOST=localhost"
if "%BLENDER_MCP_PORT%"=="" (
  echo The bootstrap recorded an empty Blender MCP bridge port.
  exit /b 3
)
if "%UV_EXE%"=="" if exist "%UV_RECORD%" set /p UV_EXE=<"%UV_RECORD%"
if not exist "%UV_EXE%" for /f "delims=" %%U in ('where uv.exe 2^>nul') do if not defined UV_FOUND set "UV_FOUND=%%U"
if defined UV_FOUND set "UV_EXE=%UV_FOUND%"
if not exist "%UV_EXE%" (
  echo uv.exe is required for the resolved latest Blender MCP route.
  exit /b 3
)
if not exist "%BLENDER_MCP_PROJECT%\pyproject.toml" (
  echo Resolved latest Blender MCP project is missing: %BLENDER_MCP_PROJECT%
  exit /b 4
)

"%UV_EXE%" --directory "%BLENDER_MCP_PROJECT%" run blender-mcp
exit /b %errorlevel%

:missing_meshy_key
echo MESHY_API_KEY is missing. Stop before starting the workflow.
echo Run:
echo [Environment]::SetEnvironmentVariable^(
echo     "MESHY_API_KEY",
echo     "msy_your_actual_key_here",
echo     "User"
echo ^)
echo Then restart the shell or Codex.
exit /b 2
