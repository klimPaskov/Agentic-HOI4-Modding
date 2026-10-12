// File helpers: read reference images as data URLs, save generated PNGs without
// clobbering existing files.

import fs from "node:fs/promises";
import path from "node:path";

const MIME_BY_EXT = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
};

// Sniff the real type from magic bytes so a mislabeled extension still works.
function sniffMime(buf, ext) {
  if (buf.length >= 8 && buf[0] === 0x89 && buf[1] === 0x50) return "image/png";
  if (buf.length >= 3 && buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff) return "image/jpeg";
  if (buf.length >= 12 && buf.toString("ascii", 0, 4) === "RIFF" && buf.toString("ascii", 8, 12) === "WEBP")
    return "image/webp";
  if (buf.length >= 6 && buf.toString("ascii", 0, 3) === "GIF") return "image/gif";
  return MIME_BY_EXT[ext.toLowerCase()] || null;
}

async function readImageAsDataUrl(filePath, baseDir) {
  const abs = path.isAbsolute(filePath) ? filePath : path.resolve(baseDir, filePath);
  const buf = await fs.readFile(abs);
  const mime = sniffMime(buf, path.extname(abs));
  if (!mime) throw new Error(`unsupported or unrecognized image file: ${abs}`);
  return `data:${mime};base64,${buf.toString("base64")}`;
}

export async function readReferenceImages(paths, baseDir) {
  return Promise.all((paths ?? []).map((p) => readImageAsDataUrl(p, baseDir)));
}

async function pathExists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

// If `requested` exists, append -v2, -v3 ... so we never overwrite.
async function pickNonOverwritePath(requested, maxVersion = 999) {
  if (!(await pathExists(requested))) return requested;
  const dir = path.dirname(requested);
  const ext = path.extname(requested);
  const stem = path.basename(requested, ext);
  for (let n = 2; n <= maxVersion; n++) {
    const candidate = path.join(dir, `${stem}-v${n}${ext}`);
    if (!(await pathExists(candidate))) return candidate;
  }
  throw new Error(`could not find a free filename under ${dir}/${stem}-vN${ext}`);
}

/**
 * Save a base64 PNG to disk, resolving `out` relative to baseDir unless absolute,
 * and versioning the name if it already exists.
 * @returns {Promise<{savedPath: string, versioned: boolean}>}
 */
export async function savePng(out, baseDir, base64) {
  const requested = path.isAbsolute(out) ? out : path.resolve(baseDir, out);
  await fs.mkdir(path.dirname(requested), { recursive: true });
  const savedPath = await pickNonOverwritePath(requested);
  await fs.writeFile(savedPath, Buffer.from(base64, "base64"));
  return { savedPath, versioned: savedPath !== requested };
}
