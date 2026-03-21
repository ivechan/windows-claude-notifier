# Windows Notification Server (Windows 桌面通知服务)

[English](README.md) | **中文文档**

一个基于 Flask 和 `win11toast` 构建的极简后台服务器组件，允许您通过发送本地 HTTP POST 请求，来触发带有自定义声音的 Windows 桌面原生系统通知（Toast）。

## 功能特性
- **原生系统级通知**: 使用轻量化的纯 Python 库 `win11toast`，完美融入 Windows 10/11 的操作中心和免打扰行为。
- **系统托盘集成**: 服务端由 `pystray` 托管在系统后台运行，无命令行黑框干扰。鼠标悬停托盘图标时可查看监听端口，右键菜单支持一键安全退出。
- **自定义铃声映射**: 可以在 API 层面上直接指定 `sound` 字段，以调用 Windows 内部预置的原生铃声（如 warning, alarm, call, mail）。
- **完全异步非阻塞**: 无论通知在屏幕上停留多久，Web API 的请求响应均会由守护线程瞬间处理并立即向客户端返回。

## 如何开始

### 配置与安装
请先确认系统中已安装了 Python 3 环境。
```bash
git clone https://github.com/ivechan/windows-claude-notifier.git
cd windows-claude-notifier
pip install -r requirements.txt
```

### 启动服务
双击目录下的 `start.bat`。

一切就绪后，此应用将在后台静默自启动。请观察电脑桌面右下角（系统任务栏托盘区域），会生成一个**蓝色方块图标**。如需终止服务，只需在此托盘图标上右击，选择 **退出 (Exit)**。

### 发送通知
您可以向本地端口接口 `http://127.0.0.1:5000/notify` 发送带有特定 Payload 的 JSON POST 请求。

**负载示例 (Payload):**
```json
{
  "title": "系统警报",
  "body": "内存占用率超过 90%！",
  "sound": "alarm"
}
```

**测试脚本大全:**
项目提供了开箱即用的测试脚本体验端对端的调用。
- **Windows CMD 环境**: 请双击或者终端运行 `test_curl.bat`。
- **Git Bash / WSL 环境**: 请在终端运行 `./test_curl.sh "我是自定义标题" "我是自定义消息"`。
