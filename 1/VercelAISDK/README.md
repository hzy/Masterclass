# 1/VercelAISDK: Tool Calling Agent

这是一个使用 Vercel AI SDK Core (`ai` 包) 构建的极简 Agent 示例。它展示了如何使用 `ToolLoopAgent` 定义工具（Tools）并让大语言模型（LLM）自主调用工具来解决问题。

## 快速开始

本项目使用 `bun` 进行依赖管理和运行。

### 前置要求

- [Bun](https://bun.sh)
- 一个兼容 OpenAI API 的本地服务（例如 `1/OpenAI` 中启动的服务），运行在 `http://localhost:8000`。

### 运行

在 `1/VercelAISDK` 目录下运行：

```bash
bun install
bun run index.ts
```

## 学习重点

### 1. ToolLoopAgent

代码使用了 `ai` 库中的 `ToolLoopAgent`，这是一个高层抽象，能够自动处理 LLM 的工具调用循环。

```typescript
const agent = new ToolLoopAgent({
  model: openai.chat("Qwen/Qwen2.5-3B-Instruct"),
  tools: {
    weather: tool({ ... }),
  },
});
```

### 2. 工具定义 (Zod Schema)

使用 `zod` 定义工具的输入 Schema，确保模型生成的参数符合预期类型。

```typescript
inputSchema: z.object({
  location: z.string().describe("The location to get the weather for"),
}),
```

### 3. 本地模型连接

通过 `createOpenAI` 的 `baseURL` 参数，我们可以轻松连接到本地运行的开源模型（如 Qwen2.5），而无需依赖 OpenAI 的官方 API。

```typescript
const openai = createOpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey: "sk-xxx",
});
```

## 延伸阅读

### Vercel AI

前往 [Vercel AI SDK](https://ai-sdk.vercel.com/) 和 [Vercel AI Elements](https://elements.ai-sdk.dev/) 了解更多 Vercel 在 AI 上的建设，大部分建设已经逐渐成为主流选择。

