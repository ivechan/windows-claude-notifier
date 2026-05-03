# AGENTS.md

## Setup
- `requirements.txt` omits `win11toast` (conditional Windows import in `app.py`). On Windows, run: `pip install win11toast`
- **Linux**: requires `python3-gi` + `gir1.2-gtk-3.0` system packages (auto-detected by `run.sh`, prompts to install)
- `run.sh` (Linux) and `run.bat` (Windows) auto-create venv + install deps — canonical way to launch

## Running
| Mode | Command |
|------|---------|
| Silent (tray only) | `pythonw app.py` / `start.bat` / `start_background.vbs` |
| Console | `python app.py` / `run.bat` / `run.sh` |
| Test notification | `./test_curl.sh "Title" "Body"` (bash) or `test_curl.bat` (CMD) |
| Test toast directly | `python test_win11toast.py` (Windows only) |

## Architecture
- `app.py` binds `0.0.0.0:5000` (all interfaces) but **restricts to private/loopback IPs** via `@app.before_request` — safer than hardcoding `127.0.0.1`
- Notifications fire in daemon threads — HTTP response is immediate
- Cross-platform: `win11toast` on Windows, `notify-send` + `canberra-gtk-play` on Linux
- **System tray**: `pystray` (Win32 API) on Windows, `Gtk.StatusIcon` (gi.repository) on Linux — right-click menu shows server info, test notification, exit. Left-click on Linux shows server IP/port.
- `LINUX_SOUND_MAP` maps sound keys to freedesktop event IDs (`message`, `message-new-instant`, `alarm-clock-elapsed`, `phone-incoming-call`, `dialog-warning`, etc.)
- Flask werkzeug logger suppressed to ERROR level

## Quirks
- `win11toast` imported inside `if IS_WINDOWS:` block — safe on Linux but won't error
- Linux tray uses `Gtk.StatusIcon` (gi.repository) — requires X11 or XWayland; Wayland users need `libayatana-appindicator` or XWayland
- Tray exit uses `os._exit(0)` — hard terminates
- `.bat` files must be pure ASCII / UTF-8 without `chcp` code-page switches
- Sound keys: `default`, `mail`, `sms`, `im`, `reminder`, `alarm`, `alarm2`, `call`, `call2`
