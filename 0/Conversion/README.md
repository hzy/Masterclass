# 0/Conversion: Minimal CLI Chatbot

这是一个基于 `Qwen/Qwen2.5-3B-Instruct` 模型的极简纯文本聊天程序。它展示了如何手动管理对话上下文以及构建大语言模型（LLM）所需的 Prompt Template。

## 快速开始

本项目使用 `uv` 进行依赖管理和运行。

### 前置要求

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (推荐)

### 运行

在 `0/Conversion` 目录下直接运行：

```bash
uv run main.py
```

首次运行会自动下载模型权重（约 6GB），请确保网络通畅。

## 交互方式

- 程序启动后，会出现 `>>>` 提示符。
- 输入内容并回车即可发送给 AI。
- AI 的回复会直接打印在下方。
- 输入 `quit` 或 `exit` 退出程序。

## 学习重点

### 1. 文本生成 Pipeline

代码使用了 Hugging Face `transformers` 库中的 `pipeline` 抽象。

```python
generator = pipeline("text-generation", model=model_id)
```

这是调用 LLM 最简单的方式，它封装了模型加载、分词（Tokenization）和后处理步骤。

### 2. 手动上下文管理 (Context Management)

LLM 本身是无状态的（Stateless）。为了实现“多轮对话”，我们需要手动维护历史记录。

```python
# 每一轮对话，我们都将之前的 history 加上新的输入，再次传给模型
history += f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
outputs = generator(history, ...)
```

这就是为什么你会看到 `history` 变量在不断累加。

### 3. Prompt Template (ChatML 格式)

现代指令微调（Instruction Tuned）模型通常需要特定的格式来区分 System、User 和 Assistant 的发言。
本项目手动构建了 Qwen/ChatML 格式的 Prompt：

```text
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
Hello<|im_end|>
<|im_start|>assistant
Hi there!<|im_end|>
```

如果不遵循这个格式，模型可能会生成混乱的内容或无法理解指令。

### 4. 生成配置 (GenerationConfig)

通过 `GenerationConfig` 我们可以控制生成的行为：

- `max_new_tokens`: 限制回复的最大长度。
- `do_sample`: 启用采样，让回答更具多样性。
- `temperature`: 控制随机性（值越高越随机）。

## 延伸学习

### 模型的 Tokenizer 的差异

在 [tiktokenizer - gpt2](https://tiktokenizer.vercel.app/?model=gpt2) 和 [tiktokenizer - Qwen/Qwen2.5-72B](https://tiktokenizer.vercel.app/?model=Qwen%2FQwen2.5-72B) 中分别输入 [3. Prompt Template](#3-prompt-template-chatml-格式)，观察 token 的区别。
