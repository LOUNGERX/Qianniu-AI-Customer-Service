千牛 AI 自动化客服系统 (Qianniu AI RPA)
本项目是一个基于 视觉感知 与 大语言模型 (LLM) 驱动的自动化客服 RPA 方案。它能够模拟人工操作，自动读取千牛客户端的聊天记录，并通过 AI 生成专业回复进行自动补全与发送。

## 项目核心亮点
视觉感知 (Vision-to-Text)：摒弃了传统的本地 OCR，采用 Qwen2.5-VL 视觉模型直接从屏幕截图中提取对话上下文，识别率更高，理解力更强。

逻辑决策 (Agent-Based)：对接 AgentHub 平台，利用专业微调或 Prompt 优化的 Agent 模拟真实客服语境进行回覆决策。

高效采集：使用 mss 库实现毫秒级屏幕采集，配合 cv2 图像匹配技术，实现聊天记录的精准触底检测与自动滚动。

安全稳健：采用 pyperclip 剪贴板中转方案，完美解决 Windows 自动化中常见的中文乱码问题。

### 技术架构
感知层 (Capture)：利用 mss 与 pygetwindow 定位千牛窗口，执行“置顶-截图-滚动-去重”操作。

认知层 (Vision)：将截图序列发送至 通义千问 (Qwen-VL)，将视觉图像转化为结构化的文本对话清单。

决策层 (Brain)：将文本清单推送至 AgentHub API，获取符合业务逻辑（如古井贡酒客服话术）的专业回复。

执行层 (Action)：通过 pyautogui 模拟鼠标点击输入框，并使用快捷键完成内容粘贴与发送。

### 环境准备
#### 1. 依赖安装
推荐在虚拟环境（如你的 rpa_env）中运行：

Bash
pip install mss pyautogui pygetwindow pyperclip opencv-python numpy openai requests
#### 2. 坐标配置
运行项目前，请确保已使用 position_d.py 获取了你当前显示器上的物理坐标，并更新至 CONFIG 中：

INPUT_POS: 聊天输入框的中心点。

SEND_BUTTON_POS: “发送”按钮的中心点。

### 快速开始
配置 API 密钥：
在 integrated_bot.py 中填入你的 QWEN_API_KEY 和 AGENTHUB_API_KEY。

打开千牛：
确保千牛客户端处于登录状态，并打开目标客户的聊天窗口。

运行脚本：

Bash
python integrated_bot.py
### 文件结构说明
integrated_bot.py: 主程序。整合了采集、识别、决策与执行的完整闭环。

position_d.py: 辅助工具。用于探测屏幕上输入框和按钮的精确坐标。

chat_history_steps/: 临时目录。用于存放 RPA 运行过程中生成的中间过程截图。

### 注意事项与免责声明
合规性：本项目仅用于技术研究与自动化效率提升，请遵守相关平台的服务协议，避免高频调用触发风控。

安全性：请勿将包含 API_KEY 的代码上传至公开仓库，建议使用环境变量进行管理。

环境依赖：由于涉及 GUI 操作，建议在固定分辨率的显示器下运行，或关闭 Windows 的缩放比例补偿。