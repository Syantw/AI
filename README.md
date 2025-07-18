# 更新记录

## 2025-07-18

### 新增：设备自动检测与友好提示
- /devices 路由：可随时查询当前本地可用的手机/模拟器设备列表。
- /execute 路由：每次执行指令前自动检测设备，无设备时直接返回友好提示，不再继续 LLM/MCP 调用。
- 设备检测优先通过 MCP 工具（mobile_list_available_devices），如失败则自动调用 adb/idevice_id 检测。
- 支持 Android、iOS 物理机和 iOS 模拟器。
- 依赖环境：需本地安装 adb（Android）、idevice_id（iOS）等命令行工具。
- 日志中会有“未检测到可用设备，请插入手机或启动模拟器。”等友好提示。

### 注意事项
- 如无设备，所有自动化指令会被优雅拦截，不会报错。
- 插入设备或启动模拟器后，/devices 会自动检测并恢复自动化能力。
- 设备检测依赖于本地环境的 adb/idevice_id 工具，请确保已安装并配置好环境变量。
- MCP 工具检测优先，兜底用系统命令，兼容性更强。

---

# meituan-agent

🚀 **AI驱动的移动端自动化系统** - 集成本地 LLM (llama3) 与 Mobile Next MCP，实现自然语言控制移动设备

本项目成功实现了**本地挂载的 llama3 模型访问 mobile next mcp server**，支持 iOS/Android 物理设备与模拟器的自动化操作，适用于移动端自动化测试、数据采集、智能体交互等多种场景。

## 🎯 项目亮点

- 🤖 **AI 驱动**: 本地 llama3 模型解析自然语言指令，自动生成设备操作序列
- 📱 **全平台支持**: iOS/Android 物理机与模拟器，跨平台自动化
- 🔗 **MCP 协议集成**: 原生支持 Model Context Protocol，与 mobile-mcp 无缝集成
- 🧩 **可扩展架构**: Python 服务端 + Node.js MCP server，模块化设计
- 🚀 **实时响应**: 支持复杂多步业务流程自动化

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   自然语言指令   │───▶│   llama3 (Ollama) │───▶│  Python Agent    │───▶│  mobile-mcp      │
│                │    │                │    │   Server        │    │   Server        │
│ "打开微信并截图"  │    │ 生成动作序列      │    │  MCP协议调用     │    │  设备操作        │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 目录结构

```
meituan-agent/
├── agent_server.py           # Python 端主服务 (Flask)
├── main.py                   # Python 端入口
├── mcp_process_manager.py    # MCP 子进程管理
├── requirements.txt          # Python 依赖
├── test_connection.py        # 连接测试脚本
├── screenshots/              # 截图存储目录
├── mobile-mcp/               # Mobile Next MCP 子模块
│   ├── src/                  # MCP server 源码
│   ├── package.json          # Node.js 依赖
│   └── README.md             # MCP 详细文档
└── README.md                 # 项目说明
```

## 🛠️ 技术栈

- **后端**: Python 3.9+, Flask
- **AI 模型**: Ollama + llama3
- **MCP Server**: Node.js + TypeScript
- **移动端**: iOS/Android (物理机/模拟器)
- **协议**: Model Context Protocol (MCP)

## 📦 安装依赖

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

- **iOS**: 需安装 Xcode 命令行工具、go-ios（`npm install -g go-ios`）
- **Android**: 需安装 Android Platform Tools
- **Ollama**: 需安装并拉取 llama3 模型（`ollama pull llama3`）

## 🚀 快速上手

### 1. 启动 Ollama 服务

```bash
# 拉取 llama3 模型（首次使用）
ollama pull llama3

# 启动 Ollama 服务
ollama serve
```

### 2. 启动 MCP 服务

```bash
cd mobile-mcp
npx -y @mobilenext/mobile-mcp@latest --port 8080
```

### 3. 启动 Python 服务

```bash
python main.py
```

### 4. 连接设备

- **iOS 物理机**: 连接设备并信任电脑，启动 go-ios tunnel
- **Android 物理机**: 开启 USB 调试，连接设备
- **模拟器**: 启动 iOS Simulator 或 Android Emulator

### 5. 发送自动化指令

```bash
# 使用 curl 发送指令
curl -X POST http://localhost:5001/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "打开微信并截图"}'

# 或使用其他 HTTP 客户端
```

## 💡 使用示例

### 基础操作

```bash
# 启动应用
{"command": "打开微信"}

# 截图
{"command": "截图"}

# 点击操作
{"command": "点击屏幕中央"}

# 输入文本
{"command": "在搜索框输入'你好'"}
```

### 复杂流程

```bash
# 多步操作
{"command": "打开微信，点击通讯录，截图保存"}

# 应用间切换
{"command": "打开美团，搜索餐厅，截图，然后回到微信"}
```

## 🔧 支持的 MCP 工具

- `mobile_launch_app` - 启动应用
- `mobile_take_screenshot` - 截图
- `mobile_click_on_screen_at_coordinates` - 点击坐标
- `mobile_type_keys` - 输入文本
- `mobile_swipe_on_screen` - 滑动操作
- `mobile_press_button` - 按键操作
- `mobile_list_apps` - 列出应用
- `mobile_list_elements_on_screen` - 列出屏幕元素

## 📊 API 接口

### POST /execute

执行自动化指令

**请求体:**
```json
{
  "command": "打开微信并截图"
}
```

**响应:**
```json
{
  "message": "Execution successful",
  "final_image": "screenshots/final_flow.png",
  "actions_executed": [...]
}
```

### GET /health

健康检查

**响应:**
```json
{
  "status": "healthy",
  "message": "Agent server is running"
}
```

## 🔍 故障排除

### 常见问题

1. **连接超时**: 检查设备是否连接，mobile-mcp 是否启动
2. **iOS 17+ 问题**: 需要启动 go-ios tunnel (`sudo ios tunnel start`)
3. **模型加载失败**: 确保 Ollama 运行且 llama3 模型已下载
4. **权限问题**: iOS 设备需要信任电脑，Android 需要开启调试

### 调试模式

启动时添加详细日志：

```bash
# Python 服务
python main.py

# MCP 服务
cd mobile-mcp && npx -y @mobilenext/mobile-mcp@latest --port 8080
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 Apache-2.0 License，详情见 [LICENSE](mobile-mcp/LICENSE)。

## 🙏 致谢

- [Mobile Next MCP](https://github.com/mobile-next/mobile-mcp) - 移动端 MCP 服务器
- [Ollama](https://ollama.ai/) - 本地 LLM 运行环境
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 协议规范

## 📞 联系方式

如有问题或建议，欢迎提交 [Issue](https://github.com/Syantw/AI/issues) 或 [Pull Request](https://github.com/Syantw/AI/pulls)。

---

**⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！** 