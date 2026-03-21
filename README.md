# Windows Notification Server

**English** | [中文文档](README_zh.md)

A minimalist background server built with Flask and `win11toast` that accepts HTTP POST requests to trigger native Windows Toast notifications (with customizable sounds).

## Features
- **Native Windows Toasts**: Uses `win11toast` to smoothly integrate with the Windows 10/11 Action Center.
- **System Tray Integration**: Quietly runs in the background using `pystray`. No command prompt windows are left open.
- **Customizable Sounds**: Send a `sound` argument in the API to trigger native Windows sound schemes (default, alarm, call, mail, etc).
- **Asynchronous Execution**: Web requests return instantly while the notification displays in a background thread.

## Getting Started

### Installation
Ensure you have Python 3 installed.
```bash
git clone https://github.com/ivechan/windows-claude-notifier.git
cd windows-claude-notifier
pip install -r requirements.txt
```

### Running the Server
Simply double click `start.bat`.

The application will launch silently in the background. Look for a blue square icon in your system tray on the lower-right taskbar. You can right-click this icon and click **退出 (Exit)** to cleanly stop the server at any time.

### Sending Notifications
Send a POST request to `http://127.0.0.1:5000/notify` with a JSON payload.

**Example Payload:**
```json
{
  "title": "Alert",
  "body": "System usage high!",
  "sound": "alarm"
}
```

**Testing:**
- **Windows CMD**: Double click `test_curl.bat`.
- **Bash / WSL**: Run `./test_curl.sh "Title" "Body"`.
