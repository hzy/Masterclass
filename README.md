# Masterclass

hzy 为 yx 准备的“私房课”。

本项目旨在通过一系列**循序渐进、最小可行**的代码示例，帮助开发者从零开始理解现代 AI 应用的开发范式。

## 学习路线

### 0. 基础篇 (Foundations)

这一部分主要通过最小代码示例，介绍 LLM 的核心概念。

* **[0/GPT2 - Hello World](./0/GPT2/)**
  * 最简单的文本生成示例。
  * 理解 Tokenization、Next Token Prediction（下一个词预测）以及 Generation Config（生成配置）。
  * **重点**: 跑通第一个模型，理解“续写”本质。

* **[0/Conversion - 聊天机器人](./0/Conversion/)**
  * 从单次续写进化到多轮对话。
  * 手动管理对话历史（Context Management）。
  * 理解 ChatML 格式（System/User/Assistant）与 Prompt Template。
  * **重点**: 学会构建 Prompt，让模型听懂指令。

* **[0/ToolCalling - 函数调用](./0/ToolCalling/)**
  * 让 LLM 主动调用外部工具（Function Calling）。
  * 理解 ReAct 模式（Reasoning + Acting）的基础。
  * **重点**: 连接外部世界，赋予 AI 行动能力。

* **[0/Compact - 上下文压缩](./0/Compact/)**
  * 使用 MLX 在 Apple Silicon 上运行长上下文 Qwen 对话。
  * 将整本《Alice's Adventures in Wonderland》注入 System Prompt，体验超长上下文。
  * 实现手动与自动 Context Compaction（上下文压缩）。
  * **重点**: 学会在有限上下文窗口内保留长期记忆。

### 1. 工程篇 (Engineering)

这一部分探讨如何将模型封装为符合生产标准的 API，并在 Web、TUI 等真实交互场景中落地。

* **[1/OpenAI - OpenAI Compatible API](./1/OpenAI/)**
  * 将模型封装为符合 OpenAI 规范的 HTTP 接口。
  * 手写 Pydantic Schema 理解 `v1/chat/completions` 协议细节。
  * 实现流式输出 (SSE) 与工具调用 (Tool Calling) 的分片传输。
  * **重点**: 让你的模型直接接入 LangChain、OpenWebUI 等生态。

* **[1/VercelAISDK - AI SDK Core Agent](./1/VercelAISDK/)**
  * 使用 Vercel AI SDK Core (`ai`) 构建极简 Agent。
  * 体验 `ToolLoopAgent` 自动处理工具调用的循环。
  * 使用 Zod 定义工具输入 Schema，无需手动解析 JSON。
  * **重点**: 掌握高层抽象 SDK 如何简化 Agent 开发。

* **[1/VercelAIElements - AI SDK UI Components](./1/VercelAIElements/)**
  * 使用 Vercel AI SDK UI (`@ai-sdk/react`) 构建现代 Chat 界面。
  * 配合 [AI Elements](https://elements.ai-sdk.dev/) 组件库快速搭建美观 UI。
  * 理解 `useChat` Hook 如何管理消息状态、流式响应与重试机制。
  * **重点**: 前后端数据流打通，实现类 ChatGPT 的流畅交互体验。

* **[1/TUIAgent - Terminal Chat Agent](./1/TUIAgent/)**
  * 使用 `Vercel AI SDK v6 + OpenTUI` 构建终端聊天 Agent。
  * 按 `message.parts` 渲染 `text / reasoning / tool`，清晰展示推理与工具状态。
  * 内置 `bash / read / write / edit` 工具，并支持审批流与安全拦截。
  * **重点**: 掌握 TUI 场景下的流式交互与工具调用可视化实践。

### 2. 协议与集成篇 (Protocols & Integrations)

这一部分聚焦协议化能力与集成实践，当前以 MCP Server 为主，后续将扩展到更多协议与连接方式。

* **[2/ToolkitMCPServer - Developer Toolkit MCP](./2/ToolkitMCPServer/)**
  * 基于 `stdio + bun + @modelcontextprotocol/sdk` 的本地工具型 MCP Server。
  * 提供 `read / write / edit / bash` 四个实用工具。
  * 演示如何将工具注册逻辑模块化拆分（`tools/` + `lib/`）。
  * **重点**: 搭建可复用的本地工程助手 MCP。

* **[2/WeatherMCPServer - Weather MCP](./2/WeatherMCPServer/)**
  * 单工具 `get_weather` 的最小天气服务示例。
  * 包含 `inputSchema` 与 `outputSchema` 的完整定义。
  * 展示文本输出与 `structuredContent` 双通道返回。
  * **重点**: 用最小代码掌握 MCP Tool 的输入输出约定。

## 环境准备

本项目推荐使用 `uv` 进行依赖管理，它能自动处理 Python 版本和虚拟环境。

1. **安装 uv**:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. **运行示例**:
    进入任意子目录，直接运行即可（uv 会自动同步依赖）：

    ```bash
    cd 0/GPT2
    uv run main.py
    ```

## 贡献

欢迎提交 PR 或 Issue 来改进代码示例或补充文档。

## License

MIT
