import sys
import os

# 保护 Windows pythonw 环境下标准输入输出流为 None 导致的异常
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

from flask import Flask, request, jsonify
from win11toast import toast
import logging
import threading
import pystray
from PIL import Image, ImageDraw

app = Flask(__name__)
# 隐藏 Flask 默认的日志，保持控制台清爽
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 常见的 Windows 系统提示音
SOUND_MAP = {
    'default': 'ms-winsoundevent:Notification.Default',
    'mail': 'ms-winsoundevent:Notification.Mail',
    'sms': 'ms-winsoundevent:Notification.SMS',
    'im': 'ms-winsoundevent:Notification.IM',
    'reminder': 'ms-winsoundevent:Notification.Reminder',
    'alarm': 'ms-winsoundevent:Notification.Looping.Alarm',
    'alarm2': 'ms-winsoundevent:Notification.Looping.Alarm2',
    'call': 'ms-winsoundevent:Notification.Looping.Call',
    'call2': 'ms-winsoundevent:Notification.Looping.Call2',
}

def show_toast_async(title, body, audio_src):
    try:
        # app_id 定义了操作中心中显示的应用名称
        toast(title, body, audio={'src': audio_src}, app_id='Claude Code')
    except Exception as e:
        print(f"弹窗失败: {e}")

@app.route('/notify', methods=['POST'])
def notify_endpoint():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "无效的 JSON 数据"}), 400
        
        title = data.get('title', '新通知')
        body = data.get('body', '')
        sound_key = data.get('sound', 'default')
        
        # 匹配声音参数
        audio_src = SOUND_MAP.get(sound_key, SOUND_MAP['default'])
        
        # 后台线程发送通知，防止阻塞 HTTP 请求响应
        threading.Thread(target=show_toast_async, args=(title, body, audio_src), daemon=True).start()
        
        print(f"[{title}] {body} (Sound: {sound_key})")
        return jsonify({"status": "success", "message": "通知请求已接收"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def run_flask():
    app.run(host='127.0.0.1', port=5000)

def create_image():
    # 生成一个简单的系统托盘图标 (蓝底白色矩形)
    image = Image.new('RGB', (64, 64), color=(0, 120, 215))
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
    return image

def on_exit(icon, item):
    icon.stop()
    os._exit(0)

if __name__ == '__main__':
    # 启动 Flask 的后台守护线程
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 初始化并启动系统托盘图标，阻塞主线程
    icon_image = create_image()
    menu = pystray.Menu(pystray.MenuItem('退出 (Exit)', on_exit))
    icon = pystray.Icon("WindowsNotifier", icon_image, "Windows 通知服务", menu)
    
    icon.run()
