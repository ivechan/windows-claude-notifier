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

# 3. opencode notification plugin
PLUGIN_SRC="opencode-plugin/notification.js"
PLUGIN_DEST="$HOME/.config/opencode/plugins/notification.js"

if [ -f "$PLUGIN_DEST" ]; then
    echo "[plugin] OpenCode 通知插件已存在，跳过安装"
else
    echo "[plugin] 安装 OpenCode 通知插件..."
    mkdir -p "$(dirname "$PLUGIN_DEST")"
    cp "$PLUGIN_SRC" "$PLUGIN_DEST"
    echo "[plugin] ✓ 插件已安装到 $PLUGIN_DEST"
fi

# 4. run
echo "[run] 启动服务..."
python app.py
