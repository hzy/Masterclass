# 0/GPT2: Hello World Text Generation

这是一个最基础的文本生成示例，展示了如何使用 Hugging Face `transformers` 库加载 GPT-2 模型并生成文本。

它的功能非常简单：**给一段话的开头，让 AI 接着写下去。**

## 快速开始

本项目使用 `uv` 进行依赖管理和运行。

### 前置要求

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (推荐)

### 运行

在 `0/GPT2` 目录下直接运行：

```bash
uv run main.py
```

首次运行会自动下载 GPT-2 模型权重（约 500MB），请确保网络通畅。

## 预期输出

程序运行后，会打印一段由 "Hello, I'm a language model," 开头的续写文本。例如：

```text
Hello, I'm a language model, not a human being. I'm a computer.
```

*(注：由于设置了随机种子，你的输出应该与此类似或完全一致)*

## 学习重点

### 1. Pipeline 抽象

这是 Hugging Face 提供的高层 API，一行代码即可加载模型和分词器：

```python
generator = pipeline("text-generation", model="openai-community/gpt2")
```

对于初学者，这是上手 LLM 最快的方式。

### 2. 文本续写 (Text Completion)

GPT-2 这种 Decoder-only 模型的核心能力就是“预测下一个 token”。
你给它 `Hello`，它预测 `,`；你给它 `Hello,`，它预测 `I`... 如此循环，直到达到长度限制。

### 3. 生成配置 (GenerationConfig)

我们显式地控制了生成参数：

- `max_new_tokens`: 限制生成的长度。
- `do_sample`: 设为 `True` 表示使用采样策略（更具创造性），而非贪婪搜索（Greedy Search）。
- `temperature`: 控制随机性。值越低越保守，值越高越放飞。

### 4. 可复现性 (Reproducibility)

```python
set_seed(42)
```

通过固定随机种子，我们确保每次运行代码生成的文本是一样的。这在调试和教学中非常重要。

## 延伸阅读

### 1. 理解 Tokenization (分词)

模型并不是直接“读”懂单词，而是将文本转换成数字序列（Tokens）。

你可以访问在线工具 **[tiktokenizer](https://tiktokenizer.vercel.app/?model=gpt2)** 来直观地体验这一过程。

试着输入 `Hello, world!`，你会看到它被切分成了几个特定的 Token ID。GPT-2 的工作本质就是根据前面的 Token ID 预测下一个 Token ID。

### 2. 大模型发展简史

从 GPT-2 到现在的 AI 爆发，经历了以下关键节点：

| 时间 | 模型 | 机构 | 参数量 | 关键词 | 历史意义 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2019 | **GPT-2** | OpenAI | 1.5B | Zero-shot | 验证了 Decoder-only 架构的可行性，开始展现零样本能力 |
| 2020 | **GPT-3** | OpenAI | 175B | Few-shot | “大力出奇迹”，参数量爆发，涌现（Emergence）现象初现 |
| 2022 | **ChatGPT** (GPT-3.5) | OpenAI | 175B+ | RLHF | 引入人类反馈强化学习，让 AI 真正能听懂指令并流畅对话 |
| 2023 | **Llama 1/2** | Meta | 7B-70B | Open Source | 点燃了开源大模型生态，让个人开发者也能在本地运行大模型 |
| 2023 | **GPT-4** | OpenAI | MoE (推测) | Reasoning | 逻辑推理与多模态能力的巅峰，至今仍是行业标杆 |
| 2024 | **Qwen 2.5** | Alibaba | 0.5B-72B | SOTA Open | 中国开源模型崛起，在各项基准测试中达到世界顶尖水平 |
| 2025 | **DeepSeek-V3** | DeepSeek | 671B (37B Active) | MoE, Cost-Effective | 探索极致性价比和混合专家架构（MoE），降低训练与推理成本 |
| 2025 | **Gemini 3 Pro** | Google | Unknown | 1M+ Context | 极长上下文窗口，能一次性读完几本书或几小时视频 |

### 3. 如何读懂模型名字

现在的模型名字越来越长，比如 `Qwen/Qwen2.5-3B-Instruct`。我们可以把它拆解来看：

#### 示例 A: 基础命名

`Qwen/Qwen2.5-3B-Instruct`

- **Qwen/**: 组织名 (Organization)。这里代表阿里云通义千问团队。
- **Qwen2.5**: 系列与版本 (Series & Version)。这是 Qwen 系列的 2.5 版本。
- **3B**: 参数量 (Size)。**3 Billion** 即 30 亿参数。参数量通常决定了模型的“智力”上限，但也决定了显存占用和计算速度。
  - 0.5B - 3B: 适合手机/端侧部署。
  - 7B - 14B: 适合消费级显卡 (RTX 3090/4090) 运行。
  - 70B+: 通常需要多卡或数据中心级显卡。
- **Instruct**: 模型类型 (Type)。
  - **Instruct / Chat**: 经过指令微调，适合对话（ChatGPT 模式）。
  - **Base**: 基础模型，只能做文本续写（GPT-2 模式），通常用于特定领域的进一步微调。

#### 示例 B: 进阶命名 (MoE 与量化)

`Qwen/Qwen2.5-Coder-32B-Instruct-AWQ` (注：以此为例解析复杂后缀)

- **Coder**: 领域特化。表示该模型针对编程代码进行了额外训练。
- **AWQ / GPTQ / Int4**: 量化格式 (Quantization)。表示模型经过了压缩。
  - 原始模型通常是 `FP16` (16位浮点数)。
  - `Int4` 表示压缩到了 4位整数，显存占用减少约 70%，但精度略有下降。

#### 示例 C: 混合专家模型 (MoE) 命名

`DeepSeek-V3` (Total 671B, Active 37B) 或假设的 `Qwen-3.5-A3B`

- **MoE (Mixture of Experts)**: 混合专家架构。
- **Total Parameters (总参数)**: 模型包含的所有参数量（如 671B），决定了知识的广度。
- **Active Parameters (激活参数)**: 生成每个 token 时实际参与计算的参数量（如 37B），决定了推理速度和成本。
- **A3B**: 这里的 "A" 通常指 **Active**。意味着虽然模型很大，但跑起来像一个小模型一样快。
