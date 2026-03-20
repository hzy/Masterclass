import { join, resolve } from "node:path";

export const defaultWorkdir = process.cwd();

export function resolveTargetPath(filePath: string, workdir: string): string {
  return filePath.startsWith("/")
    ? resolve(filePath)
    : resolve(join(workdir, filePath));
}
