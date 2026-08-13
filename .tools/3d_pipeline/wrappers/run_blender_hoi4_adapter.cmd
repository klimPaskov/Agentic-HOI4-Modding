@echo off
setlocal

if not defined MESHY_API_KEY goto missing_meshy_key

set "PIPELINE_ROOT=%~dp0.."
set "ADAPTER_ROOT=%PIPELINE_ROOT%\adapter"
set "HOI4_3D_CONFIG=%PIPELINE_ROOT%\config\blender_hoi4_adapter.json"

if not "%UV_EXE%"=="" goto uv_selected
for /f "delims=" %%U in ('where uv.exe 2^>nul') do if not defined UV_EXE set "UV_EXE=%%U"
:uv_selected
if not exist "%UV_EXE%" (
    echo uv.exe is required for the repository-owned Blender HOI4 adapter.
    exit /b 3
)
if not exist "%ADAPTER_ROOT%\pyproject.toml" (
    echo Blender HOI4 adapter project is missing: %ADAPTER_ROOT%
    exit /b 4
)
if not exist "%HOI4_3D_CONFIG%" (
    echo Generated Blender HOI4 adapter config is missing. Run bootstrap_3d_workflow.py first.
    exit /b 5
)

"%UV_EXE%" --directory "%ADAPTER_ROOT%" run python -m hoi4_blender_mcp %*
exit /b %errorlevel%

:missing_meshy_key
echo MESHY_API_KEY is missing. Stop before starting the 3D workflow.
exit /b 2
