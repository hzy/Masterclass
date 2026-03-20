# 2/ToolkitMCPServer: Toolkit MCP (stdio)

这是一个基于 `@modelcontextprotocol/sdk` 的本地 MCP Server 示例，使用 `stdio` 传输、`bun` 运行，提供一组实用的开发工具：`read / write / edit / bash`。

## 核心特性

1. **stdio MCP Server**: 可直接被 Claude Desktop、Cursor 等支持 MCP 的客户端拉起。
2. **文件工具集**:
   - `read`: 读取文件或目录，支持 `offset/limit` 分段查看
   - `write`: 写入完整文件内容，可自动创建父目录
   - `edit`: 执行 `oldString -> newString` 替换，且要求唯一匹配
3. **终端工具**: `bash` 支持 `workdir`、`timeoutMs`、输出截断。
4. **基础安全策略**: `bash` 内置危险命令模式拦截（如 `rm -rf /`、fork bomb、`shutdown` 等）。
5. **结构化代码**: 工具注册、通用返回、路径处理已拆分，入口文件保持精简。

## 快速开始

在 `2/ToolkitMCPServer` 目录下执行：

```bash
bun install
bun run start
```

开发模式（文件变更自动重启）：

```bash
bun run dev
```

启动成功后会看到日志：`toolkit-mcp server started on stdio`

## MCP Server 信息

- `name`: `toolkit-mcp`
- `version`: `1.0.0`
- `title`: `Toolkit MCP`
- `instructions`: 引导客户端优先 `read` 再 `edit/write`，并避免破坏性 shell 操作

## 工具说明

### `read`

- 入参：`filePath`, `workdir`, `offset`, `limit`
- 能力：
  - 读取目录时返回条目列表（目录名带 `/`）
  - 读取文件时按行返回，并附带行号

### `write`

- 入参：`filePath`, `content`, `workdir`, `overwrite`, `createParentDirs`
- 能力：整文件写入，默认允许覆盖并自动创建父目录

### `edit`

- 入参：`filePath`, `oldString`, `newString`, `workdir`
- 能力：严格单次替换（`oldString` 必须且只能出现一次）

### `bash`

- 入参：`command`, `description`, `timeoutMs`, `workdir`
- 返回：`ok`, `exitCode`, `stdout`, `stderr`, `durationMs`, `timedOut`, `truncated`
- 安全：拦截高危命令模式，避免误伤主机

## 目录结构

```text
2/ToolkitMCPServer
├─ src/
│  ├─ index.ts
│  ├─ lib/
│  │  ├─ toolResult.ts
│  │  └─ workspace.ts
│  └─ tools/
│     ├─ registerBashTool.ts
│     └─ registerFileSystemTools.ts
├─ package.json
├─ tsconfig.json
└─ README.md
```

## 与 MCP 客户端集成（示例）

不同客户端配置格式略有差异，核心是通过 `bun` 启动该 server，并使用 `stdio`。

示例命令：

```bash
bun run /absolute/path/to/2/ToolkitMCPServer/src/index.ts
```

你也可以在客户端配置里直接使用：

- `command`: `bun`
- `args`: `run`, `/absolute/path/to/2/ToolkitMCPServer/src/index.ts`

## 说明

- 当前实现偏教学和本地开发用途，默认信任本地调用环境。
- 若用于团队共享或更高安全要求场景，建议增加路径白名单、命令策略和审计日志。
