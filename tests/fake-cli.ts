import { chmod, mkdir, writeFile } from "node:fs/promises"
import { join } from "node:path"

export async function installFakeCli(binDir: string): Promise<void> {
  await mkdir(binDir, { recursive: true })
  await Promise.all([writeFake(binDir, "aws"), writeFake(binDir, "kubectl"), writeFake(binDir, "helm")])
}

async function writeFake(binDir: string, name: string): Promise<void> {
  const filePath = join(binDir, name)
  await writeFile(
    filePath,
    `#!/usr/bin/env node
const fs = require("node:fs");
if (process.env.EKS_FAKE_CLI_LOG) {
  fs.appendFileSync(process.env.EKS_FAKE_CLI_LOG, JSON.stringify({ binary: ${JSON.stringify(name)}, args: process.argv.slice(2) }) + ${JSON.stringify("\n")});
}
const payload = { binary: ${JSON.stringify(name)}, args: process.argv.slice(2), awsKey: "AKIA1234567890ABCDEF" };
process.stdout.write(JSON.stringify(payload));
`,
    "utf8"
  )
  await chmod(filePath, 0o755)
}
