# 0/ToolCalling: Function Calling with LLMs

这个示例展示了如何让大语言模型（LLM）不仅仅是生成文本，而是**主动调用外部工具**（Function Calling）。

这是构建 Agent（智能体）的基石。通过这种方式，模型可以获取实时数据（如天气）、执行操作（如发邮件）或查询数据库。

## 核心概念

1. **Tool Definition**: 向模型描述有哪些工具可用（名称、功能、参数格式）。
2. **Tool Selection**: 模型根据用户问题，决定是否调用工具，以及调用哪个工具。
3. **Tool Execution**: 代码拦截模型的调用请求，在本地执行函数。
4. **Observation**: 将函数执行结果反馈给模型。
5. **Final Response**: 模型根据工具返回的结果，生成最终回答。

## 快速开始

### 前置要求

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- **注意**: 本代码默认配置为 macOS (Apple Silicon) 使用 `mps` 加速。如果你是 Windows/Linux (CUDA) 或纯 CPU，请修改 `main.py` 中的 `device_map`。

### 运行

在 `0/ToolCalling` 目录下：

```bash
uv run main.py
```

### 预期输出

你会看到一个完整的工具调用闭环：

```text
👨‍💻 用户: What's the weather like in Beijing today?

🤖 模型请求调用工具: get_weather, 参数: Beijing
[本地系统] 🔧 正在执行工具: get_weather, 参数: Beijing
[本地系统] 🔧 工具执行结果: Sunny, 25°C

🤖 最终回答: The weather in Beijing today is sunny with a temperature of 25°C.
```

## 代码解析

### 1. 定义工具 (Schema)

我们用 JSON Schema 格式告诉模型有一个 `get_weather` 函数：

```python
tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather...",
            "parameters": { ... }
        }
    }
]
```

### 2. 注入工具信息

使用 `apply_chat_template` 将工具定义注入到 System Prompt 中：

```python
text = tokenizer.apply_chat_template(
    messages, 
    tools=tools_definition,  # 关键点
    add_generation_prompt=True
)
```

### 3. 解析与执行

模型不会真的去执行代码，它只是**生成一段文本**（通常是 JSON），表示它想调用的函数。

我们需要：

1. 捕获这段 JSON。
2. 解析出函数名和参数。
3. 在 Python 中执行真正的 `get_weather` 函数。
4. 将结果（`Sunny, 25°C`）作为新的 Message 反馈给模型。

## 延伸思考

- **多步调用**: 如果用户问 "北京和伦敦的天气哪个更好？"，模型需要调用两次 `get_weather` 吗？
- **错误处理**: 如果模型生成的 JSON 格式错误怎么办？
- **安全性**: 允许模型执行任意代码（如 `os.system`）是非常危险的，如何限制？

这个简单的例子展示了 ReAct (Reasoning + Acting) 循环中最基础的一环。
