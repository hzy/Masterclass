# 2/MCPInspector: Model Context Protocol Inspector

本章节主要介绍并演示如何使用官方提供的 MCP Inspector 工具来调试和检查你的 MCP Server。
在使用代码进行复杂的 Client-Server 联调之前，MCP Inspector 提供了一个极佳的图形化界面，让你直观地“看”到你的 MCP Server 暴露了哪些能力、以及调用返回的结果。

## 为什么需要 MCP (Model Context Protocol)？

在运行代码之前，我们需要先弄清楚：**MCP 究竟是用来解决什么问题的？**

### 1. 痛点：N × M 的集成地狱

在过去，如果我们要给各种 AI 应用（比如 Claude Desktop、Cursor、或者你自己写的 Agent）接入外部能力（比如读写本地文件、查询企业内部 API、连接数据库），我们需要为**每一个应用**针对**每一个工具**专门写一套定制的胶水代码。
假设市场上有 $N$ 种 AI 客户端，$M$ 种外部数据源，那么整个生态就需要维护 $N \times M$ 个集成接口。这不仅极其低效，而且随着工具和模型的爆炸式增长，这种方式根本无法持续。

### 2. 解决方案：AI 时代的 "USB-C" 接口

MCP (Model Context Protocol) 就是为了打破这个僵局而生的。它由 Anthropic 开源，旨在成为 AI 模型与外部数据/工具通信的**通用标准协议**。

通过 MCP，我们将复杂的网状连接变成了清晰的客户端-服务端架构：

- **MCP Server**（服务端）：负责连接具体的数据源或工具（例如我们这里的“天气服务API”），并将其能力以标准格式暴露出来。
- **MCP Client**（客户端）：任何支持 MCP 协议的 AI 应用，只需连接到 Server，就能直接“理解”并调用这些工具，完全不需要关心底层 API 是如何鉴权或请求的。

### 3. 使用 MCP 带来了什么好处？

- **一次编写，到处运行**：我们写好 MCP Server 之后，它不仅能被你自己写的脚本调用，还可以直接零配置无缝接入到 Claude Desktop、Cursor、Cline 等所有支持 MCP 的超级终端里。
- **关注点分离**：让 AI 客户端专心搞“思考”和“规划”，让 MCP Server 专心搞“执行”和“数据获取”。
- **安全与可控**：MCP Server 往往运行在本地或受信任的环境中，作为开发者，你可以严格定义和审计 AI 究竟能访问哪些资源。

## 什么是 MCP Inspector

MCP Inspector 相当于 MCP Server 的一个通用测试客户端。
它提供了一个可交互的 Web UI，允许你：

- 连接到任意本地运行的 MCP Server（支持 `stdio`、`streamableHttp` 和 `sse`）
- 浏览该 Server 提供的所有 Tools、Resources、Prompts
- 手动输入参数并调用这些工具，直观查看返回的 JSON 结果和内容
- 查看完整的请求/响应日志流，这在排查通信问题时非常有用

## 快速开始

在 `2/MCPInspector` 目录下，首先安装依赖：

```bash
bun install
```

*(或者使用 `npm install`)*

然后，你可以使用 `npx` 直接启动 MCP Inspector，后接需要启动 MCP Server 的命令。

### 检查 Weather MCP Server

假设你已经写好了后面的 `WeatherMCPServer`，并为它安装了依赖（`bun install`），可以这样启动并检查它：

```bash
npx @modelcontextprotocol/inspector bun run ../WeatherMCPServer/src/index.ts
```

运行后，Inspector 会在控制台输出一个本地 URL（通常是 `http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=xxxx`）。
打开浏览器访问该地址：

1. 点击 Connect 开始连接。
2. 切换到 "Tools" 页面，你会看到暴露的工具。
3. 点击某个工具（比如 `get_weather`），在输入框中填入参数并点击 Run 运行，即可看到结果。

### 检查 Toolkit MCP Server

同样的，如果你想要检查提供了多个工具的 `ToolkitMCPServer`（需要为它安装依赖（`bun install`））：

```bash
npx @modelcontextprotocol/inspector bun run ../ToolkitMCPServer/src/index.ts
```

> **提示：** 如果你想调试其他的 MCP Server 实现，只需要把后面的启动命令 `bun run ...` 替换成对应的执行指令（如 `node index.js` 或 `python main.py`）即可。

## 延伸阅读

1. 如果你要用 Inspector 调试 `streamableHttp` 类型的 MCP Server（而不只是本地 `stdio`），建议先看：
   - MCP Inspector 使用文档：<https://modelcontextprotocol.io/docs/tools/inspector>
   - MCP Transports 概览（`stdio` / `streamableHttp` / `sse`）：<https://modelcontextprotocol.io/docs/concepts/transports>
   - TypeScript SDK Server 文档（传输方式）：<https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/server.md#transports>
2. 你可以把 Inspector 当作“通用 HTTP MCP 客户端”，去连接远程的 `streamableHttp` 服务（例如飞书、麦当劳这类线上 MCP Server）：
   - 先单独启动 Inspector：`npx @modelcontextprotocol/inspector`
   - 在 Web UI 中把传输方式切到 `streamableHttp`，填入目标 MCP Server URL
      - 飞书的类似于：`https://mcp.larkoffice.com/mcp/mcp_${your_token}`
      - 麦当劳的类似于：`https://mcp.mcd.cn`，但是需要 `Authorization` 这个 Header 来鉴权
   - 如果服务要求鉴权，在 Headers 中添加 `Authorization: Bearer <token>` 等认证信息后再 Connect
