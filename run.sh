#!/usr/bin/env bash
set -e

VENV_DIR="venv"
REQUIREMENTS="requirements.txt"

# 1. venv
if [ ! -d "$VENV_DIR" ]; then
    echo "[setup] 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# 2. deps (skip if already satisfied)
if ! python -c "import flask, pystray, PIL" 2>/dev/null; then
    echo "[setup] 安装依赖..."
    pip install -r "$REQUIREMENTS" --quiet
fi

# 3. run
echo "[run] 启动服务..."
python app.py
