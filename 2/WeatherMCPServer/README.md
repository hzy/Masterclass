# 2/WeatherMCPServer: Weather MCP (stdio)

这是一个基于 `@modelcontextprotocol/sdk` 的天气 MCP Server 示例，使用 `stdio` 传输、`bun` 运行，对外提供一个简洁的天气查询工具 `get_weather`。

## 为什么需要 MCP (Model Context Protocol)？

在运行这段代码之前，我们需要先弄清楚：**MCP 究竟是用来解决什么问题的？**

### 1. 痛点：N × M 的集成地狱
在过去，如果我们要给各种 AI 应用（比如 Claude Desktop、Cursor、或者你自己写的 Agent）接入外部能力（比如读写本地文件、查询企业内部 API、连接数据库），我们需要为**每一个应用**针对**每一个工具**专门写一套定制的胶水代码。
假设市场上有 $N$ 种 AI 客户端，$M$ 种外部数据源，那么整个生态就需要维护 $N \times M$ 个集成接口。这不仅极其低效，而且随着工具和模型的爆炸式增长，这种方式根本无法持续。

### 2. 解决方案：AI 时代的 "USB-C" 接口
MCP (Model Context Protocol) 就是为了打破这个僵局而生的。它由 Anthropic 开源，旨在成为 AI 模型与外部数据/工具通信的**通用标准协议**。

通过 MCP，我们将复杂的网状连接变成了清晰的客户端-服务端架构：
- **MCP Server**（服务端）：负责连接具体的数据源或工具（例如我们这里的“天气服务API”），并将其能力以标准格式暴露出来。
- **MCP Client**（客户端）：任何支持 MCP 协议的 AI 应用，只需连接到 Server，就能直接“理解”并调用这些工具，完全不需要关心底层 API 是如何鉴权或请求的。

### 3. 使用 MCP 带来了什么好处？
* **一次编写，到处运行**：我们写好这个 `WeatherMCPServer` 之后，它不仅能被你自己写的脚本调用，还可以直接零配置无缝接入到 Claude Desktop、Cursor、Cline 等所有支持 MCP 的超级终端里。
* **关注点分离**：让 AI 客户端专心搞“思考”和“规划”，让 MCP Server 专心搞“执行”和“数据获取”。
* **安全与可控**：MCP Server 往往运行在本地或受信任的环境中，作为开发者，你可以严格定义和审计 AI 究竟能访问哪些资源。

在这个 `WeatherMCPServer` 示例中，我们将体验如何用极简的代码，提供一个标准的、带严格输入输出约束的 MCP 工具节点。


## 核心特性

1. **stdio MCP Server**: 可被支持 MCP 的客户端直接拉起并调用。
2. **单工具最小实现**: 聚焦一个工具 `get_weather`，便于理解 MCP Tool 的输入输出约定。
3. **结构化输出**: 同时返回可读文本和 `structuredContent`，方便客户端展示与后处理。
4. **轻量实现**: 保持实现简洁，便于快速接入和联调 MCP 客户端。

## 快速开始

在 `2/WeatherMCPServer` 目录下执行：

```bash
bun install
bun run start
```

开发模式（文件变更自动重启）：

```bash
bun run dev
```

启动成功后会看到日志：`weather-mcp server started on stdio`

## MCP Server 信息

- `name`: `weather-mcp`
- `version`: `1.0.0`
- `title`: `Weather MCP`
- `instructions`: 提示客户端通过 `get_weather` 获取天气快照，并通过 `unit` 控制温度单位

## 工具说明

### `get_weather`

- 入参：
  - `city`（必填）：城市名，例如 `Shanghai`
  - `country`（可选）：国家或地区
  - `unit`（可选）：`celsius` 或 `fahrenheit`，默认 `celsius`
- 输出字段：
  - `city`, `country`
  - `condition`（`sunny/cloudy/rainy/windy/snowy`）
  - `temperature`, `unit`
  - `humidity`, `windKph`
  - `note`

## 目录结构

```text
2/WeatherMCPServer
├─ src/
│  └─ index.ts
├─ package.json
├─ tsconfig.json
└─ README.md
```

## 与 MCP 客户端集成（示例）

核心思路是通过 `bun` 启动该 server，并使用 `stdio` 作为传输层。

示例命令：

```bash
bun run /absolute/path/to/2/WeatherMCPServer/src/index.ts
```

客户端配置中通常可映射为：

- `command`: `bun`
- `args`: `run`, `/absolute/path/to/2/WeatherMCPServer/src/index.ts`

## 数据流转（Agent / MCP Client / MCP Server）

下面用两个阶段说明典型交互链路：

1. `initialize` 阶段：客户端与服务端完成能力协商（协议版本、capabilities、server info）。
2. `tool call` 阶段：Agent 先让 MCP Client `list_tools`，再发起 `tools/call(get_weather)`，最终把结果返回给用户。

```mermaid
sequenceDiagram
    participant User as 用户
    participant Agent as Agent
    participant Client as MCP Client
    participant Server as Weather MCP Server

    Note over Client,Server: Transport = stdio（Client 写入 Server stdin，读取 Server stdout）

    User->>Agent: 问天气（如 "Shanghai weather"）
    Agent->>Client: 连接并准备调用 MCP

    rect rgb(245, 248, 255)
      Note over Client,Server: 阶段1：initialize
      Client->>Server: initialize(request)\n(JSON-RPC over stdio)
      Server-->>Client: initialize(response: serverInfo/capabilities)\n(JSON-RPC over stdio)
      Client->>Server: notifications/initialized\n(JSON-RPC notification over stdio)
    end

    rect rgb(245, 255, 248)
      Note over Agent,Server: 阶段2：tool call
      Agent->>Client: 请求可用工具
      Client->>Server: tools/list\n(JSON-RPC over stdio)
      Server-->>Client: tools(list: get_weather)\n(JSON-RPC over stdio)

      Agent->>Client: 调用 get_weather(city, country?, unit?)
      Client->>Server: tools/call(get_weather)\n(JSON-RPC over stdio)
      Server-->>Client: tool result(content + structuredContent)\n(JSON-RPC over stdio)
      Client-->>Agent: 标准化工具结果
    end

    Agent-->>User: 返回天气结果
```

## 说明

- 当前示例为教学用途，优先展示 MCP Tool 的输入输出与接入方式。
- 若要接入外部天气服务，可在 `src/index.ts` 中替换数据来源并保留当前 tool schema。

## 延伸阅读

1. MCP 不仅可以提供工具（Tools），还可以提供 Prompts、Resources、Events，甚至支持 Sampling 等能力。可以从下面几个入口继续看：
   - MCP 官方文档首页：<https://modelcontextprotocol.io/introduction>
   - MCP 规范（Specification）：<https://spec.modelcontextprotocol.io>
   - TypeScript SDK 文档（Server 能力总览）：<https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/server.md>
   - TypeScript SDK 能力文档（Sampling / Elicitation / Tasks）：<https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/capabilities.md>
2. MCP 也可以使用不同于 `stdio` 的传输方式，例如 Streamable HTTP（推荐）以及兼容场景下的 SSE。可参考：
   - MCP Transports 概览：<https://modelcontextprotocol.io/docs/concepts/transports>
   - TypeScript SDK Server 文档（stdio / Streamable HTTP / SSE）：<https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/server.md#transports>
3. HTTP 版本的 MCP Server 可以接入复杂多样的鉴权方式（如 Bearer Token、OAuth 2.0、client credentials、JWT 等），并允许使用 session 机制来支持有状态场景（如会话上下文、订阅流、任务恢复）。可参考：
   - MCP Authorization 规范：<https://modelcontextprotocol.io/specification/draft/basic/authorization>
   - MCP Transports 与 Session 概览：<https://modelcontextprotocol.io/docs/concepts/transports>
   - TypeScript SDK Server 文档（OAuth / 认证相关）：<https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/server.md#authentication-and-authorization>
   - TypeScript SDK Client 文档（OAuth 客户端示例）：<https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/client.md#oauth>
