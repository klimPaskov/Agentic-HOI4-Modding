#!/usr/bin/env node
// One-shot image generation from the command line. Handy for testing and as a
// Bash-callable fallback when MCP isn't wired up.
//
//   node src/gen.js --prompt "a red fox in snow" --out fox.png
//   node src/gen.js -p "edit this" -o out.png --ref a.png --ref b.png --quality high --size 1024x1024

import { getValidCredentials } from "./auth.js";
import { generateImage } from "./codex.js";
import { readReferenceImages, savePng } from "./images.js";

function parseArgs(argv) {
  const out = { refs: [], quality: "high", baseDir: process.cwd() };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => argv[++i];
    if (a === "--prompt" || a === "-p") out.prompt = next();
    else if (a === "--out" || a === "-o") out.out = next();
    else if (a === "--ref" || a === "--reference") out.refs.push(next());
    else if (a === "--quality" || a === "-q") out.quality = next();
    else if (a === "--size" || a === "-s") out.size = next();
  }
  return out;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.prompt || !args.out) {
    console.error('Usage: node src/gen.js --prompt "..." --out path.png [--ref img.png] [--quality high] [--size 1024x1024]');
    process.exit(2);
  }
  const creds = await getValidCredentials();
  const referenceDataUrls = await readReferenceImages(args.refs, args.baseDir);
  process.stderr.write("Generating image...\n");
  const base64 = await generateImage(creds, {
    prompt: args.prompt,
    quality: args.quality,
    size: args.size,
    referenceDataUrls,
  });
  const { savedPath, versioned } = await savePng(args.out, args.baseDir, base64);
  console.log(savedPath + (versioned ? " (versioned to avoid overwrite)" : ""));
}

main().catch((err) => {
  console.error("✗ " + (err?.message || err));
  process.exit(1);
});
