# 0/Compact: Context Compaction with MLX

这是一个基于 `mlx-lm` 构建的长上下文对话示例。它展示了如何在 Apple Silicon 上加载 `Qwen/Qwen2.5-3B-Instruct`，将整本《Alice's Adventures in Wonderland》注入 System Prompt，并在上下文接近极限时自动进行压缩（Context Compaction）。

和前面的 `0/Conversion` 不同，这个示例关注的不是“如何开始多轮对话”，而是“当对话越来越长时，如何在有限上下文窗口里保留长期记忆”。

## 快速开始

本项目使用 `uv` 进行依赖管理和运行。

### 前置要求

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (推荐)
- Apple Silicon Mac（推荐，`mlx-lm` 依赖 MLX）

### 运行

在 `0/Compact` 目录下直接运行：

```bash
uv run main.py
```

首次运行会自动下载模型权重，请确保网络通畅。

如果你更习惯使用脚本，也可以运行：

```bash
./run.sh
```

## 交互方式

- 程序启动后，会先加载模型和 `alice.txt` 中的小说全文。
- 输入任意内容并回车，即可与 Alice 对话。
- 输入 `/compact` 可手动触发一次上下文压缩。
- 输入 `/quit` 或 `/exit` 退出程序。

## 学习重点

### 1. 长上下文角色扮演

程序会将整本小说作为 System Prompt 的一部分传给模型：

```python
system_prompt = (
    "You are Alice from Lewis Carroll's 'Alice's Adventures in Wonderland'. "
    "Answer all questions as Alice would, staying in character. "
    "Use the following text as your memory and world knowledge:\n\n"
    f"{novel_text}"
)
```

这种写法很直接，但也会快速消耗上下文窗口，因此非常适合作为“上下文管理”教学示例。

### 2. Token 计数与阈值监控

程序并不是等到模型报错才处理，而是每轮对话后主动统计当前上下文的 token 数量：

```python
current_tokens = count_tokens(messages, tokenizer)
if current_tokens > COMPACTION_THRESHOLD:
    messages = compact_context(messages, tokenizer, model)
```

这对应了真实工程里的常见做法：在接近上限时提前做裁剪、摘要或分段处理。

### 3. Context Compaction（上下文压缩）

压缩逻辑的核心思想是：

- 保留最重要的 System Prompt
- 保留最近几轮对话
- 将更早的历史消息总结成一段摘要

代码中通过再次调用模型，把旧消息总结成一条新的 system message：

```python
new_messages = [messages[0]]
new_messages.append(
    {"role": "system", "content": f"[Previous Conversation Summary]: {summary}"}
)
new_messages.extend(messages[end_index:])
```

这是一种最基础但非常实用的“长期记忆压缩”策略。

### 4. MLX 与流式输出

本示例使用 `mlx-lm` 提供的 `load`、`generate` 和 `stream_generate` 接口：

- `load(...)`: 加载模型与 tokenizer
- `generate(...)`: 用于生成摘要
- `stream_generate(...)`: 用于主对话的流式输出

相比通用的 PyTorch 示例，这种方案更适合在 Apple Silicon 上体验长上下文推理。

## 延伸阅读

### 1. 为什么需要上下文压缩

LLM 的上下文窗口并不是无限的。即使模型支持 64k、128k 甚至更长的上下文，随着对话增长：

- 推理速度会下降
- 显存 / 内存占用会上升
- 无关历史会稀释真正重要的信息

因此，“让模型记住所有历史”通常不是最优解，“保留关键信息并压缩冗余内容”才是更实际的工程策略。

### 2. 压缩并不等于删除

压缩的本质不是简单截断，而是做一次“信息重编码”：

- 截断：丢掉旧消息，最简单，但容易失忆
- 摘要：保留关键事实，成本低，最常见
- 检索：把历史放到外部存储中，按需取回

这个示例实现的是第二种，也是多数 Agent 系统的入门版本。

### 3. 从 Compaction 走向 Memory / RAG / Agent

如果继续沿着这个方向往下学，你会自然过渡到更完整的系统设计：

- **Memory**: 不再只保留摘要，而是区分短期记忆和长期记忆
- **RAG**: 不把全部知识塞进 Prompt，而是按需检索相关片段
- **Agent**: 结合工具调用、规划和记忆机制，让模型在更长任务链中持续工作

所以，`0/Compact` 虽然代码很小，但它已经在触碰现代 AI 应用里非常核心的一类问题。
