import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import * as z from "zod/v4";
import { asTextResult } from "../lib/toolResult.js";

const dangerousPattern =
  /(rm\s+-rf\s+\/($|\s)|mkfs\.|:\(\)\{\s*:\|:\s*&\s*\};:|shutdown\s|reboot\s|halt\s)/i;

const maxOutputChars = 8000;

function trimOutput(value: string): { text: string; truncated: boolean } {
  if (value.length <= maxOutputChars) {
    return { text: value, truncated: false };
  }

  return {
    text: `${value.slice(0, maxOutputChars)}\n... output truncated ...`,
    truncated: true,
  };
}

export function registerBashTool(server: McpServer): void {
  server.registerTool(
    "bash",
    {
      description:
        "Run a bash command and return stdout/stderr/exit code. Use for local terminal tasks.",
      inputSchema: {
        command: z.string().min(1).describe("Shell command to execute"),
        description: z
          .string()
          .min(3)
          .max(80)
          .describe("Short purpose of this command"),
        timeoutMs: z
          .number()
          .int()
          .min(1000)
          .max(120000)
          .default(120000)
          .describe("Command timeout in milliseconds"),
        workdir: z
          .string()
          .default(process.cwd())
          .describe("Working directory to execute in"),
      },
    },
    async ({ command, timeoutMs, workdir }) => {
      const startedAt = Date.now();

      if (dangerousPattern.test(command)) {
        return asTextResult({
          ok: false,
          exitCode: null,
          timedOut: false,
          cwd: workdir,
          durationMs: 0,
          stdout: "",
          stderr:
            "Blocked dangerous command pattern (rm -rf /, mkfs, fork bomb, shutdown/reboot/halt).",
          truncated: false,
        });
      }

      try {
        const proc = Bun.spawn(["bash", "-lc", command], {
          cwd: workdir,
          stdout: "pipe",
          stderr: "pipe",
        });

        const timedResult = await Promise.race([
          proc.exited.then((exitCode) => ({ type: "exit" as const, exitCode })),
          new Promise<{ type: "timeout" }>((resolvePromise) => {
            setTimeout(() => resolvePromise({ type: "timeout" }), timeoutMs);
          }),
        ]);

        if (timedResult.type === "timeout") {
          proc.kill();
          return asTextResult({
            ok: false,
            exitCode: null,
            timedOut: true,
            cwd: workdir,
            durationMs: Date.now() - startedAt,
            stdout: "",
            stderr: `Command timed out after ${timeoutMs}ms`,
            truncated: false,
          });
        }

        const [stdoutRaw, stderrRaw] = await Promise.all([
          new Response(proc.stdout).text(),
          new Response(proc.stderr).text(),
        ]);

        const stdout = trimOutput(stdoutRaw);
        const stderr = trimOutput(stderrRaw);

        return asTextResult({
          ok: timedResult.exitCode === 0,
          exitCode: timedResult.exitCode,
          timedOut: false,
          cwd: workdir,
          durationMs: Date.now() - startedAt,
          stdout: stdout.text,
          stderr: stderr.text,
          truncated: stdout.truncated || stderr.truncated,
        });
      } catch (error) {
        return asTextResult({
          ok: false,
          exitCode: null,
          timedOut: false,
          cwd: workdir,
          durationMs: Date.now() - startedAt,
          stdout: "",
          stderr: error instanceof Error ? error.message : "Unknown bash error",
          truncated: false,
        });
      }
    },
  );
}
