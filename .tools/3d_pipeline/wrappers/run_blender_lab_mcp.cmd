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

set "BLENDER_MCP_PROJECT=%PIPELINE_ROOT%\vendor\blender_mcp\mcp"
if "%UV_EXE%"=="" set "UV_EXE=C:\Program Files\Python313\Scripts\uv.exe"
if not exist "%UV_EXE%" for /f "delims=" %%U in ('where uv.exe 2^>nul') do if not defined UV_FOUND set "UV_FOUND=%%U"
if defined UV_FOUND set "UV_EXE=%UV_FOUND%"
if not exist "%UV_EXE%" (
  echo uv.exe is required for the locked Blender MCP route.
  exit /b 3
)
if not exist "%BLENDER_MCP_PROJECT%\pyproject.toml" (
  echo Locked Blender MCP project is missing: %BLENDER_MCP_PROJECT%
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
