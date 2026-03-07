# 1/OpenAI - OpenAI Compatible API (Real Model)

本章节展示如何将 **真实的 LLM (Qwen2.5-3B)** 封装为符合 OpenAI 规范的 HTTP 接口，并支持 **Tool Calling**。

## 核心特性

1. **真实模型**: 使用 Hugging Face `transformers` 加载 `Qwen/Qwen2.5-3B-Instruct`。
2. **流式生成**: 使用 `TextIteratorStreamer` 实现真实的打字机效果。
3. **Tool Calling**: 利用 System Prompt 引导模型输出 JSON，并实时流式传输给客户端。
4. **硬件加速**: 默认配置为 Apple Silicon (`mps`) 加速。

## 依赖说明

本项目使用 `uv` 管理依赖。由于引入了 PyTorch 和 Transformers，首次运行会下载较大的依赖包。

1. **启动服务端**:

    ```bash
    cd 1/OpenAI
    # 首次运行会自动下载模型权重 (~6GB)，请确保网络通畅
    uv run server.py
    ```

    *注意*: 如果你是 Linux/Windows 用户，请修改 `engine.py` 中的 `DEVICE` 为 `cuda` 或 `cpu`。

2. **运行测试客户端**:

    ```bash
    cd 1/OpenAI
    uv run client.py
    ```

## 实现原理

* **engine.py**: 负责模型加载、Chat Template 应用、System Prompt 注入（用于 Tool Calling），以及流式生成逻辑。
* **server.py**: FastAPI 服务，负责将 `engine` 的输出封装为 OpenAI SSE 格式 (`data: {...}`).
* **protocol.py**: 定义了 Pydantic Schema，确保 JSON 结构完全兼容。

## 观察重点

当你运行 `client.py` 询问天气时：

1. **engine.py** 会检测到 Prompt 中包含 Tools。
2. 它会在 System Prompt 中注入 Tool 定义，告诉 Qwen "如果要用工具，请输出 JSON"。
3. 当 Qwen 生成 `{ "name": ...` 时，`engine.py` 会识别出这是 Tool Call。
4. `server.py` 会将这些内容标记为 `tool_calls` 而不是普通 `content`，发送给 Client。

## 延伸阅读 (Extended Reading)

虽然本章节实现了最经典的 OpenAI `v1/chat/completions` 接口，但 AI 接口的世界远不止于此。

1. **接口的多样性**:
    * **OpenAI**: 除了经典的 Chat 接口，还在探索更新的 `/responses` 接口（以及 Realtime API 等）。
    * **Anthropic**: 采用 `/v1/messages` 接口，它在 Message 结构上更严格（如必须 User/Assistant 交替）。
    * **Google Gemini**: 采用 RESTful 风格更重的 URL，例如 `/v1/models/gemini-3-pro-preview-new:streamGenerateContent?alt=sse`。

2. **殊途同归**:
    尽管 URL 和 JSON 字段名各异，但它们的核心抽象惊人地一致：都基于 `Role` (角色)、`Content` (内容)、以及流式传输的 `Delta` (增量) 概念。

3. **接口桥接 (Bridging)**:
    这种一致性使得“接口适配器”成为可能。你可以编写中间件，将一种格式转化为另一种。
    * *例如*：你可以把 **GPT-5.3-Codex** 这样的模型，通过适配层“伪装”成 Claude 的接口格式；或者把 Google 的 Gemini 包装成 OpenAI 兼容接口（如本项目所做），从而让同一套客户端代码无缝切换底层模型。

4. **工业级实现 (Industrial Implementation)**:
    想要了解生产环境中的 `/chat/completions` 接口是如何实现的吗？推荐阅读 **[vLLM](https://github.com/vllm-project/vllm)** 的源码。
    *   **入口**: [`vllm/entrypoints/openai/api_server.py`](https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/openai/api_server.py)
    *   **核心逻辑**: [`vllm/entrypoints/openai/serving_chat.py`](https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/openai/serving_chat.py)

    vLLM 是目前最流行的开源推理框架之一。不同于本项目的极简实现，它在服务端处理了 **Continuous Batching** (连续批处理)、**PagedAttention** (分页注意力)、**Distributed Inference** (分布式推理) 等复杂问题，以实现极高的吞吐量和低延迟。但你会发现，其顶层的接口定义与协议处理逻辑，与本项目是高度一致的。

5. **端侧实现 (On-Device Implementation)**:
    如果你对在 CPU 或移动设备上运行感兴趣，**[llama.cpp](https://github.com/ggerganov/llama.cpp)** 是必读的经典。
    *   **核心逻辑**: [`examples/server/server.cpp`](https://github.com/ggerganov/llama.cpp/blob/master/examples/server/server.cpp)
    
    llama.cpp 展示了如何用 C++ 从零构建一个高性能的 OpenAI 兼容服务器。通过 **GGUF 量化** 技术，它能让庞大的 LLM 在消费级 CPU 甚至手机上流畅运行。这里的实现更加底层，让你看到即使是不同编程语言，对于 `chat/completions` 协议的实现也是殊途同归的。
