# 0/Multimodal: Visual Language Models

这是一个多模态大语言模型（MLLM）的基础示例，展示了如何使用 `Qwen2.5-VL-3B-Instruct` 处理图像输入。

它的功能非常直观：**给模型一张图片和一段文本指令，让它描述或回答关于图片的问题。**

本项目旨在揭示多模态模型输入层的“黑盒”机制，特别是图像在 ChatML 格式和 Token 序列中的具体表现形式。

## 快速开始

本项目使用 `uv` 进行依赖管理和运行。

### 前置要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (推荐)
- 足够的硬盘空间（下载模型约需 6GB）
- 建议使用 GPU（CUDA/MPS）以获得合理的推理速度，但在 CPU 上也能运行（较慢）。

### 运行

在 `0/Multimodal` 目录下直接运行：

```bash
uv run main.py
```

首次运行会自动下载：
1. 一张示例图片（HTTP 404 Cat）。
2. Qwen2.5-VL-3B-Instruct 模型权重（约 6GB）。

## 预期输出

程序运行后，会分阶段打印处理过程的中间状态，最后输出模型的推理结果：

```text
=== 1. High-Level Input (Messages) ===
... (Python List of Dicts) ...

=== 2. ChatML Prompt (Text Representation) ===
<|im_start|>system...<|vision_start|><|image_pad|><|vision_end|>...

=== 3. Processing Inputs (Tensor Level) ===
Input IDs shape: torch.Size([1, 600+]) ...

=== 5. Running Inference (Loading Model...) ===
Model Output: The image typically displays a cat hiding under a piece of paper...
```

## 学习重点

### 1. 多模态输入构建 (High-Level)

在代码层面，我们将图像和文本封装在一个消息列表中。不同于纯文本模型，这里的 `content` 是一个列表，包含不同类型的元素：

```python
{
    "role": "user",
    "content": [
        {"type": "image", "image": "example.jpg"},
        {"type": "text", "text": "Describe this image."},
    ],
}
```

这是目前主流多模态 API（如 OpenAI GPT-4V, Anthropic Claude 3）通用的格式。

### 2. ChatML 中的图像占位符

模型接收的本质上还是“文本”（Token 序列）。Qwen2.5-VL 使用特殊的 Tag 来标记图像的位置：

```text
<|vision_start|><|image_pad|><|vision_end|>
```

在 Prompt Template 阶段，无论图片多大，它在文本字符串中只表现为一个简单的占位符。这让 Prompt 的结构保持清晰。

### 3. 动态分辨率 (Dynamic Resolution)

Qwen2.5-VL 的核心特性之一是**Dynamic Resolution**。

- 传统模型（如 CLIP）通常将图片强制缩放到固定大小（如 224x224）。
- Qwen2.5-VL 会根据图片的实际长宽比和分辨率，将其切分为不同数量的 Patch。
- 代码中的 `inputs.image_grid_thw` 展示了这种动态网格信息。

### 4. Token 展开 (The Real Input)

这是本示例最核心的展示部分。

当 Processor 将 ChatML 转换为 Input IDs 时，那个单一的 `<|image_pad|>` 占位符会被**展开**成数百甚至数千个 `<|image_pad|>` Token。

```text
<|vision_start|><|image_pad|><|image_pad|>... (数百个) ...<|image_pad|><|vision_end|>
```

这些 Token 的位置直接对应了图像 Patch 的特征向量。模型在进行 Self-Attention 计算时，就是通过这些 Token “看见”图像的。

## 延伸阅读

### 1. Vision Encoder 与 Projector

多模态模型通常由三部分组成：
1.  **Vision Encoder** (如 ViT, SigLIP): 负责“看”图，把像素变成特征向量。
2.  **Projector** (如 MLP, C-Abstractor): 负责“翻译”，把视觉特征映射到语言模型的 Token 空间。
3.  **LLM Backbone** (如 Qwen2.5): 负责“思考”和生成文本。

`process_vision_info` 和 `processor` 的工作就是前两步的准备阶段。

### 2. 为什么是 Qwen2.5-VL?

在开源多模态领域，Qwen-VL 系列目前（2024-2025）处于领先地位：
- **原生分辨率**: 支持任意分辨率输入，不再糊图。
- **长视频理解**: 可以处理长达 1 小时的视频（通过抽取大量帧）。
- **强大的 OCR**: 能精准识别图片中的密集文本。

### 3. 多模态的未来

从 `0/GPT2` 的纯文本生成，到 `0/Multimodal` 的图文理解，我们正处于 AI 感知能力快速融合的阶段。未来的模型将不仅能“看”，还能“听”（Audio）、“说”（Speech Output）甚至“动”（Action Output，如操作手机）。
