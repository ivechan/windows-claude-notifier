import sys
import os
import platform
import subprocess
import shutil
import ipaddress
import logging
import threading
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw

IS_WINDOWS = platform.system() == 'Windows'

if IS_WINDOWS:
    import pystray
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')
    from win11toast import toast
else:
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        gi.require_version('GdkPixbuf', '2.0')
        from gi.repository import Gtk, GLib, GdkPixbuf
    except (ImportError, ValueError) as e:
        print(f"错误: 需要安装 GTK3 开发库 - {e}")
        print("Ubuntu/Debian: sudo apt install python3-gi gir1.2-gtk-3.0")
        print("Fedora: sudo dnf install python3-gobject gtk3")
        print("Arch: sudo pacman -S python-gobject gtk3")
        sys.exit(1)

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
    image = Image.new('RGBA', (64, 64), (0, 120, 215, 255))
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill=(255, 255, 255, 255))
    return image

def send_test_notification():
    threading.Thread(target=show_toast_async, args=("测试通知", "右键菜单正常工作 ✓"), daemon=True).start()

def show_server_info():
    threading.Thread(target=show_toast_async, args=("Claude Code Notifier", "0.0.0.0:5000\n服务运行中 ✓"), daemon=True).start()

# ---- Windows tray (pystray) ----
if IS_WINDOWS:
    def run_tray():
        icon_image = create_image()
        menu = pystray.Menu(
            pystray.MenuItem('Claude Code Notifier (0.0.0.0:5000)', None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('发送测试通知', lambda: send_test_notification()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('退出 (Exit)', lambda icon, item: os._exit(0))
        )
        icon = pystray.Icon("ClaudeCodeNotifier", icon_image,
                            "Claude Code Notifier (0.0.0.0:5000)", menu)
        icon.run()

# ---- Linux tray (GTK StatusIcon) ----
else:
    def pil_to_pixbuf(img):
        img = img.convert('RGBA')
        data = img.tobytes()
        w, h = img.size
        return GdkPixbuf.Pixbuf.new_from_bytes(
            GLib.Bytes.new(data),
            GdkPixbuf.Colorspace.RGB,
            True, 8, w, h, w * 4
        )

    def run_tray():
        pixbuf = pil_to_pixbuf(create_image())

        icon = Gtk.StatusIcon()
        icon.set_from_pixbuf(pixbuf)
        icon.set_tooltip_text("Claude Code Notifier (0.0.0.0:5000)")

        menu = Gtk.Menu()

        info = Gtk.MenuItem(label="Claude Code Notifier (0.0.0.0:5000)")
        info.set_sensitive(False)
        menu.append(info)

        menu.append(Gtk.SeparatorMenuItem())

        test = Gtk.MenuItem(label="发送测试通知")
        test.connect("activate", lambda _: send_test_notification())
        menu.append(test)

        menu.append(Gtk.SeparatorMenuItem())

        exit_item = Gtk.MenuItem(label="退出 (Exit)")
        exit_item.connect("activate", lambda _: os._exit(0))
        menu.append(exit_item)

        menu.show_all()

        icon.connect("popup-menu", lambda i, b, t: menu.popup(None, None, None, None, b, t))
        icon.connect("activate", lambda _: show_server_info())

        Gtk.main()

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    run_tray()
