#!/usr/bin/env node
// MCP server exposing image generation to Claude Code (and any MCP client).
// Talks over stdio. Auth is resolved lazily per call, so the server starts even
// before you've signed in.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { getValidCredentials, loadAuth, planFromToken } from "./auth.js";
import { generateImage } from "./codex.js";
import { readReferenceImages, savePng } from "./images.js";

// Claude Code does not pass a working directory to MCP tools, so resolve relative
// output/reference paths against the project root it launched us in.
const PROJECT_DIR = process.env.GPTIMAGE_PROJECT_DIR || process.cwd();

const server = new McpServer({ name: "gptimage", version: "0.1.0" });

server.tool(
  "generate_image",
  [
    "Generate a raster image (PNG) from a text prompt using the ChatGPT subscription image model.",
    "Use for AI-created bitmap visuals: photos, illustrations, textures, sprites, icons, mockups, backgrounds.",
    "Optionally pass reference images (paths) to guide style/subject/composition — describe each one's role in the prompt, e.g. 'Image 1 is the character, Image 2 is the background style'.",
    "Generates ONE image per call. For multiple distinct assets, call once per asset.",
    "Returns the absolute path of the saved PNG. Billed to the user's ChatGPT plan, not an API key.",
  ].join(" "),
  {
    prompt: z.string().describe("Detailed description of the image to generate. Be specific about subject, style, colors, composition, lighting."),
    out: z.string().describe("Output file path (relative to the project directory unless absolute). A .png is written; an existing file is auto-versioned, never overwritten."),
    quality: z.enum(["low", "medium", "high", "auto"]).optional().describe("Generation quality. Default: high."),
    size: z.string().optional().describe("'auto' or WIDTHxHEIGHT (e.g. 1024x1024, 1536x1024, 1024x1536). Multiples of 16, max edge 3840, ratio <= 3:1."),
    reference_images: z.array(z.string()).optional().describe("Optional reference image paths (relative to project dir unless absolute) used to guide generation."),
  },
  async ({ prompt, out, quality, size, reference_images }) => {
    try {
      const creds = await getValidCredentials();
      const referenceDataUrls = await readReferenceImages(reference_images, PROJECT_DIR);
      const base64 = await generateImage(creds, { prompt, quality: quality || "high", size, referenceDataUrls });
      const { savedPath, versioned } = await savePng(out, PROJECT_DIR, base64);
      return {
        content: [
          {
            type: "text",
            text: `Image saved to ${savedPath}${versioned ? " (the requested path existed, so this was versioned)" : ""}.`,
          },
        ],
      };
    } catch (err) {
      return { isError: true, content: [{ type: "text", text: `Image generation failed: ${err?.message || err}` }] };
    }
  },
);

server.tool(
  "image_auth_status",
  "Check whether gptimage is authenticated with a ChatGPT account, and via which store. Call this if generation fails with an auth error.",
  {},
  async () => {
    const record = await loadAuth();
    if (!record) {
      return {
        content: [
          {
            type: "text",
            text: "Not authenticated. The user must run `npm run login` in the gptimage directory (sign in with their ChatGPT account), or have the Codex CLI logged in (`codex login`).",
          },
        ],
      };
    }
    const plan = planFromToken(record.access) ?? "unknown";
    return {
      content: [
        {
          type: "text",
          text: `Authenticated. source=${record.store}, plan=${plan}, accountId=${record.accountId ?? "unknown"}.`,
        },
      ],
    };
  },
);

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("gptimage MCP server running (stdio).");
