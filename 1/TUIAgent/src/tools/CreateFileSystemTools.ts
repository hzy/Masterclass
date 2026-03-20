import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { tool } from "ai";
import { z } from "zod";

const defaultWorkdir = process.cwd();

function resolveTargetPath(filePath: string, workdir: string): string {
  return filePath.startsWith("/") ? resolve(filePath) : resolve(join(workdir, filePath));
}

export const createReadTool = () =>
  tool({
    description:
      "Read a file or directory. Supports optional line range for text files.",
    inputSchema: z.object({
      filePath: z.string().min(1).describe("Absolute path or path relative to workdir"),
      workdir: z.string().default(defaultWorkdir),
      offset: z.number().int().min(1).default(1),
      limit: z.number().int().min(1).max(2000).default(200),
    }),
    needsApproval: true,
    execute: async ({ filePath, workdir, offset, limit }) => {
      const targetPath = resolveTargetPath(filePath, workdir);

      try {
        const targetStat = await stat(targetPath);

        if (targetStat.isDirectory()) {
          const entries = await readdir(targetPath, { withFileTypes: true });
          const lines = entries
            .map((entry) => (entry.isDirectory() ? `${entry.name}/` : entry.name))
            .sort((a, b) => a.localeCompare(b));

          return {
            ok: true,
            path: targetPath,
            type: "directory",
            content: lines.join("\n"),
            totalLines: lines.length,
            returnedLines: lines.length,
            truncated: false,
          };
        }

        const raw = await readFile(targetPath, "utf8");
        const allLines = raw.split("\n");
        const startIndex = Math.max(0, offset - 1);
        const endIndex = Math.min(allLines.length, startIndex + limit);
        const view = allLines
          .slice(startIndex, endIndex)
          .map((line, index) => `${startIndex + index + 1}: ${line}`);

        return {
          ok: true,
          path: targetPath,
          type: "file",
          content: view.join("\n"),
          totalLines: allLines.length,
          returnedLines: view.length,
          truncated: endIndex < allLines.length,
        };
      } catch (error) {
        return {
          ok: false,
          path: targetPath,
          error: error instanceof Error ? error.message : "Read failed",
        };
      }
    },
  });

export const createWriteTool = () =>
  tool({
    description:
      "Write full file content. Creates parent directories when needed.",
    inputSchema: z.object({
      filePath: z.string().min(1).describe("Absolute path or path relative to workdir"),
      content: z.string().describe("Full content to write"),
      workdir: z.string().default(defaultWorkdir),
      overwrite: z.boolean().default(true),
      createParentDirs: z.boolean().default(true),
    }),
    needsApproval: true,
    execute: async ({ filePath, content, workdir, overwrite, createParentDirs }) => {
      const targetPath = resolveTargetPath(filePath, workdir);

      try {
        if (createParentDirs) {
          await mkdir(dirname(targetPath), { recursive: true });
        }

        if (!overwrite) {
          try {
            await stat(targetPath);
            return {
              ok: false,
              path: targetPath,
              error: "File already exists and overwrite=false",
            };
          } catch {
            // file does not exist, continue
          }
        }

        await writeFile(targetPath, content, "utf8");

        return {
          ok: true,
          path: targetPath,
          bytesWritten: Buffer.byteLength(content, "utf8"),
        };
      } catch (error) {
        return {
          ok: false,
          path: targetPath,
          error: error instanceof Error ? error.message : "Write failed",
        };
      }
    },
  });

export const createEditTool = () =>
  tool({
    description:
      "Edit a file by replacing oldString with newString. oldString must appear exactly once.",
    inputSchema: z.object({
      filePath: z.string().min(1).describe("Absolute path or path relative to workdir"),
      oldString: z.string().min(1).describe("String to find. Must be unique in file."),
      newString: z.string().describe("Replacement string"),
      workdir: z.string().default(defaultWorkdir),
    }),
    needsApproval: true,
    execute: async ({ filePath, oldString, newString, workdir }) => {
      const targetPath = resolveTargetPath(filePath, workdir);

      try {
        const original = await readFile(targetPath, "utf8");

        let firstIndex = original.indexOf(oldString);
        if (firstIndex === -1) {
          return {
            ok: false,
            path: targetPath,
            error: "oldString not found",
            matchCount: 0,
          };
        }

        let matchCount = 0;
        while (firstIndex !== -1) {
          matchCount += 1;
          firstIndex = original.indexOf(oldString, firstIndex + oldString.length);
        }

        if (matchCount !== 1) {
          return {
            ok: false,
            path: targetPath,
            error: "oldString must be unique",
            matchCount,
          };
        }

        const updated = original.replace(oldString, newString);
        await writeFile(targetPath, updated, "utf8");

        return {
          ok: true,
          path: targetPath,
          matchCount,
          bytesWritten: Buffer.byteLength(updated, "utf8"),
        };
      } catch (error) {
        return {
          ok: false,
          path: targetPath,
          error: error instanceof Error ? error.message : "Edit failed",
        };
      }
    },
  });
