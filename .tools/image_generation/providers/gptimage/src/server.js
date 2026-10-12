#!/usr/bin/env node
// MCP server exposing image generation to Claude Code (and any MCP client).
// Talks over stdio. Auth is resolved lazily per call, so the server starts even
// before you've signed in.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { getValidCredentials, loadAuth, planFromToken } from "./auth.js";
import { generateImage } from "./codex.js";
import { ensureReferencesDir, listReferences, readReferenceImages, savePng } from "./images.js";

// Claude Code does not pass a working directory to MCP tools, so resolve relative
// output/reference paths against the project root it launched us in.
const PROJECT_DIR = process.env.GPTIMAGE_PROJECT_DIR || process.cwd();

const server = new McpServer({ name: "gptimage", version: "0.1.0" });

server.tool(
  "generate_image",
  [
    "Generate a raster image (PNG) from a text prompt using the ChatGPT subscription image model.",
    "Use for AI-created bitmap visuals: photos, illustrations, textures, sprites, icons, mockups, backgrounds.",
    "The model is far better at TRANSFORMING reference images than creating from scratch: before the first generation, ask the user for reference images (or offer to source some from the web, e.g. Pinterest/Dribbble), store them in a references/ folder at the project root, and pass their paths in reference_images. Describe each one's role in the prompt, e.g. 'Image 1 is the character, Image 2 is the background style'. Generate from scratch only when no reference can be obtained.",
    "When iterating, ask the user for feedback screenshots, save them into references/, and pass them plus the previous output as reference_images.",
    "Generates ONE image per call. For multiple distinct assets, call once per asset.",
    "Returns the absolute path of the saved PNG. Billed to the user's ChatGPT plan, not an API key.",
  ].join(" "),
  {
    prompt: z.string().describe("Detailed description of the image to generate. Be specific about subject, style, colors, composition, lighting."),
    out: z.string().describe("Output file path (relative to the project directory unless absolute). A .png is written; an existing file is auto-versioned, never overwritten."),
    quality: z.enum(["low", "medium", "high", "auto"]).optional().describe("Generation quality. Default: high."),
    size: z.string().optional().describe("'auto' or WIDTHxHEIGHT (e.g. 1024x1024, 1536x1024, 1024x1536). Multiples of 16, max edge 3840, ratio <= 3:1."),
    reference_images: z.array(z.string()).optional().describe("Reference image paths (relative to project dir unless absolute) used to guide generation. Strongly recommended — transforming references beats generating from scratch. Convention: keep them in references/ at the project root."),
  },
  async ({ prompt, out, quality, size, reference_images }) => {
    try {
      const creds = await getValidCredentials();
      await ensureReferencesDir(PROJECT_DIR);
      const existingRefs = await listReferences(PROJECT_DIR);
      const usedRefsCount = (reference_images ?? []).length;
      const referenceDataUrls = await readReferenceImages(reference_images, PROJECT_DIR);
      const base64 = await generateImage(creds, { prompt, quality: quality || "high", size, referenceDataUrls });
      const { savedPath, versioned } = await savePng(out, PROJECT_DIR, base64);
      const notes = [];
      if (versioned) notes.push("the requested path existed, so this was versioned");
      if (usedRefsCount === 0 && existingRefs.length > 0) {
        notes.push(
          `no reference_images were passed, but references/ contains ${existingRefs.length} image(s) (${existingRefs
            .slice(0, 5)
            .join(", ")}${existingRefs.length > 5 ? ", ..." : ""}) — GPT Image 2 works better transforming references than generating from scratch; consider re-running with reference_images set`,
        );
      } else if (usedRefsCount === 0 && existingRefs.length === 0) {
        notes.push(
          "no reference_images passed and references/ is empty — for best results, ask the user for reference images (or offer to source some from Pinterest/Dribbble) and drop them into references/ before iterating",
        );
      }
      const suffix = notes.length ? ` (${notes.join("; ")})` : "";
      return {
        content: [
          {
            type: "text",
            text: `Image saved to ${savedPath}${suffix}.`,
          },
        ],
      };
    } catch (err) {
      return { isError: true, content: [{ type: "text", text: `Image generation failed: ${err?.message || err}` }] };
    }
  },
);

server.tool(
  "list_references",
  "List image files in the project's references/ folder (created on demand). Use before generate_image to discover existing references that can guide the next generation. Reference-driven transforms beat text-only prompts.",
  {},
  async () => {
    try {
      await ensureReferencesDir(PROJECT_DIR);
      const refs = await listReferences(PROJECT_DIR);
      if (refs.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: "references/ is empty. Ask the user for reference images (style samples, brand assets, screenshots, sketches) or offer to source some (Pinterest/Dribbble/Behance) and save them into references/ before generating.",
            },
          ],
        };
      }
      return {
        content: [
          {
            type: "text",
            text: `references/ contains ${refs.length} image(s):\n${refs.map((r) => `- ${r}`).join("\n")}\n\nPass the relevant ones as reference_images and describe each one's role in the prompt.`,
          },
        ],
      };
    } catch (err) {
      return { isError: true, content: [{ type: "text", text: `list_references failed: ${err?.message || err}` }] };
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
