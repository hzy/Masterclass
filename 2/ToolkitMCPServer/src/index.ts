import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { registerBashTool } from "./tools/registerBashTool.js";
import { registerFileSystemTools } from "./tools/registerFileSystemTools.js";

const server = new McpServer(
  {
    name: "toolkit-mcp",
    version: "1.0.0",
    title: "Toolkit MCP",
  },
  {
    instructions:
      "Use read to inspect files or directories, write to replace full file contents, edit for single unique string replacement, and bash for terminal commands. Prefer read before edit/write, always set workdir explicitly when needed, and avoid destructive shell operations.",
  },
);

registerFileSystemTools(server);
registerBashTool(server);

const transport = new StdioServerTransport();
await server.connect(transport);

console.error("toolkit-mcp server started on stdio");
