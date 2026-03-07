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

### 1. 进阶篇 (Advanced) - *Coming Soon*

*(待补充：RAG、Agent 框架、多模态等内容)*

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
