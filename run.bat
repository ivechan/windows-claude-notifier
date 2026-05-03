@echo off
setlocal

set VENV_DIR=venv
set REQUIREMENTS=requirements.txt

if not exist "%VENV_DIR%" (
    echo [setup] 创建虚拟环境...
    python -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"

echo [check] 检查依赖...
python -c "import flask, pystray, PIL" 2>nul
if %ERRORLEVEL% neq 0 (
    echo [setup] 安装依赖...
    pip install -r "%REQUIREMENTS%" --quiet
)
pip show win11toast >nul 2>&1 || pip install win11toast --quiet

echo [run] 启动服务...
python app.py
