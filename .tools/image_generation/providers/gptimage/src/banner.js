// Prints the GPTImage pixel-art banner (pre-rendered ANSI truecolor half-blocks).
// banner.txt is a committed artifact built by scripts/build-banner.mjs — no deps here.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const BANNER = path.join(path.dirname(fileURLToPath(import.meta.url)), "banner.txt");

export function printBanner() {
  try {
    process.stdout.write(fs.readFileSync(BANNER, "utf8"));
  } catch {
    process.stdout.write("\n  G P T I M A G E — image generation for Claude Code\n\n");
  }
}
