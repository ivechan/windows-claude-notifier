import sys
import os
import platform
import subprocess
import shutil
import ipaddress
from flask import Flask, request, jsonify
import logging
import threading
import pystray
from PIL import Image, ImageDraw

IS_WINDOWS = platform.system() == 'Windows'

if IS_WINDOWS:
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')
    from win11toast import toast

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.before_request
def restrict_to_lan():
    addr = ipaddress.ip_address(request.remote_addr)
    if not (addr.is_private or addr.is_loopback):
        return jsonify({"status": "error", "message": "仅允许局域网连接"}), 403

WINDOWS_SOUND_MAP = {
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

LINUX_SOUND_MAP = {
    'default': 'message',
    'mail': 'message-new-instant',
    'sms': 'message-new-instant',
    'im': 'message-new-instant',
    'reminder': 'alarm-clock-elapsed',
    'alarm': 'phone-incoming-call',
    'alarm2': 'phone-incoming-call',
    'call': 'phone-incoming-call',
    'call2': 'phone-incoming-call',
}

def show_toast_async(title, body, sound_key='default'):
    try:
        if IS_WINDOWS:
            audio_src = WINDOWS_SOUND_MAP.get(sound_key, WINDOWS_SOUND_MAP['default'])
            toast(title, body, audio={'src': audio_src}, app_id='Claude Code')
        else:
            subprocess.run(
                ['notify-send', '--app-name=Claude Code', title, body],
                check=True, timeout=5
            )
            event_id = LINUX_SOUND_MAP.get(sound_key)
            if event_id and shutil.which('canberra-gtk-play'):
                subprocess.run(
                    ['canberra-gtk-play', '--id', event_id],
                    timeout=10
                )
    except Exception as e:
        print(f"通知发送失败: {e}")

@app.route('/notify', methods=['POST'])
def notify_endpoint():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "无效的 JSON 数据"}), 400

        title = data.get('title', '新通知')
        body = data.get('body', '')
        sound_key = data.get('sound', 'default')

        threading.Thread(target=show_toast_async, args=(title, body, sound_key), daemon=True).start()

        print(f"[{title}] {body}")
        return jsonify({"status": "success", "message": "通知请求已接收"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def run_flask():
    app.run(host='0.0.0.0', port=5000)

def create_image():
    image = Image.new('RGB', (64, 64), color=(0, 120, 215))
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
    return image

def on_exit(icon, item):
    icon.stop()
    os._exit(0)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    icon_image = create_image()
    menu = pystray.Menu(pystray.MenuItem('退出 (Exit)', on_exit))
    app_name = "Claude Code Notifier (0.0.0.0:5000)"
    icon = pystray.Icon("ClaudeCodeNotifier", icon_image, app_name, menu)

    icon.run()
