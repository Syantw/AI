# meituan-agent

本项目集成了 Python 端自动化服务与 [Mobile Next MCP](https://github.com/mobile-next/mobile-mcp) 子模块，支持 iOS/Android 物理设备与模拟器的自动化操作，适用于移动端自动化测试、数据采集、智能体交互等多种场景。

## 项目亮点

- 📱 支持 iOS/Android 物理机与模拟器的自动化操作
- 🤖 兼容 LLM/Agent 框架，支持多步业务流程自动化
- 🧩 Python 服务端可扩展，便于与各类 AI/自动化平台集成
- 🏗️ 内置 [mobile-mcp](https://github.com/mobile-next/mobile-mcp) 子模块，原生支持移动端 accessibility/screenshot 自动化

## 目录结构

```
meituan-agent/
├── agent_server.py           # Python 端主服务
├── main.py                   # Python 端入口
├── mcp_process_manager.py    # MCP 子进程管理
├── requirements.txt          # Python 依赖
├── test_connection.py        # 连接测试脚本
├── screenshots/              # 截图存储目录
├── mobile-mcp/               # Mobile Next MCP 子模块
└── ...
```

## 安装依赖

### 1. Python 依赖

```bash
pip install -r requirements.txt
```

### 2. Node.js 依赖（mobile-mcp）

```bash
cd mobile-mcp
npm install
```

### 3. 其他平台依赖

- iOS: 需安装 Xcode 命令行工具、go-ios（`npm install -g go-ios`）
- Android: 需安装 Android Platform Tools

## 快速上手

1. 启动 MCP 服务（以 mobile-mcp 为例）：

   ```bash
   cd mobile-mcp
   npx -y @mobilenext/mobile-mcp@latest
   ```

2. 启动 Python 服务：

   ```bash
   python main.py
   ```

3. 连接你的物理设备或模拟器，按需配置 tunnel（详见 mobile-mcp/README.md）。

## 主要功能

- 移动端原生 App 自动化（启动、操作、数据采集等）
- 支持 LLM/Agent 自动化脚本
- 可扩展的 Python 服务端，便于自定义业务逻辑
- 兼容多平台（iOS/Android，物理机/模拟器）

## 参考文档

- [mobile-mcp/README.md](mobile-mcp/README.md) —— 子模块详细用法
- [Mobile MCP 官方 Wiki](https://github.com/mobile-next/mobile-mcp/wiki)
- [go-ios 项目](https://github.com/danielpaulus/go-ios)

## License

本项目采用 Apache-2.0 License，详情见 [LICENSE](mobile-mcp/LICENSE)。 