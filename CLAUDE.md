# CLAUDE.md - AI Agent Guidelines

## Project Context
This is a lightweight Flask web server that triggers native Windows Toast notifications. 
The system runs silently via `pystray` in the Windows System Tray to provide a seamless background experience.

## Build and Run Commands
- **Environment Setup**: `pip install -r requirements.txt`
- **Run Server (Silent)**: `cmd /c start.bat` or `pythonw app.py`
- **Run Server (Console)**: `python app.py`
- **Testing**: `./test_curl.sh "Custom Title" "Body"` or `test_curl.bat` for CMD.

## Code Style & Architecture
- **Web Layer**: Flask `app.py` exposes a single `/notify` POST endpoint. Port is fixed to `5000` and safely bound to `127.0.0.1` so notifications cannot be triggered over the external network.
- **Notifications**: Triggered asynchronously via a daemon thread using `win11toast` to avoid blocking HTTP responses.
- **Tray Icon**: The main thread handles `pystray.Icon.run()`. We use `Pillow` to generate the icon image on-the-fly (`create_image()`) to avoid depending on external `.ico` images.
- **Formatting**: Adhere to standard Python PEP8. Ensure CLI commands are tested for Windows robustness.
- **Encoding Requirements**: When modifying Windows Batch files (`.bat`), ensure they remain standard ASCII-compatible or pure UTF-8 without mixing code-pages (`chcp`) inside, as it can corrupt execution flow in standard command prompts.
