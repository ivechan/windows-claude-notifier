#!/usr/bin/env bash
set -e

VENV_DIR="venv"
REQUIREMENTS="requirements.txt"

# 1. system deps (GTK3 for system tray)
if ! python3 -c "import gi" 2>/dev/null; then
    echo "[setup] 安装系统依赖 (python3-gi / gir1.2-gtk-3.0)..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3-gi gir1.2-gtk-3.0
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3-gobject gtk3
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm python-gobject gtk3
    else
        echo "[setup] 警告: 无法自动安装系统依赖，请手动安装:"
        echo "  Ubuntu/Debian: sudo apt install python3-gi gir1.2-gtk-3.0"
        echo "  Fedora:        sudo dnf install python3-gobject gtk3"
        echo "  Arch:          sudo pacman -S python-gobject gtk3"
    fi
fi

# 2. save system gi site-packages path (for venv fallback)
GI_SITE=$(python3 -c "
import gi, os; print(os.path.dirname(os.path.dirname(gi.__file__)))
" 2>/dev/null || echo "")

# 3. venv
if [ ! -d "$VENV_DIR" ]; then
    echo "[setup] 创建虚拟环境..."
    python3 -m venv --system-site-packages "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# 4. ensure gi is accessible inside venv
if ! python -c "import gi" 2>/dev/null; then
    if [ -n "$GI_SITE" ]; then
        export PYTHONPATH="$GI_SITE:$PYTHONPATH"
        echo "[setup] 已链接系统 GI 库 ($GI_SITE)"
    else
        echo "[setup] 错误: 找不到系统 gi 模块。请确保已安装 python3-gi / gir1.2-gtk-3.0"
        exit 1
    fi
fi

# 5. pip deps (skip if already satisfied)
if ! python -c "import flask" 2>/dev/null; then
    echo "[setup] 安装依赖..."
    pip install -r "$REQUIREMENTS" --quiet
fi

# 6. opencode notification plugin
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

# 7. run
echo "[run] 启动服务..."
python app.py
