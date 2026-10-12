// Image generation via the Codex backend `responses` endpoint.
//
// We POST a single-turn request to the same endpoint the Codex CLI uses, and
// force the hosted `image_generation` tool. The image comes back as base64 PNG
// inside the SSE stream (item.type === "image_generation_call").
//
// Reference for the request shape / endpoint:
//   https://github.com/openai/codex (codex-rs/core/src/client.rs)
//   https://github.com/yuji-hatakeyama/opencode-gpt-imagegen (src/codex.ts)

const CODEX_RESPONSES_ENDPOINT = "https://chatgpt.com/backend-api/codex/responses";

// Codex model slug that carries the hosted image_generation tool. Override with
// GPTIMAGE_MODEL if OpenAI rotates the subscription model name.
const DEFAULT_MODEL = process.env.GPTIMAGE_MODEL || "gpt-5.5";

// Client identifier sent to the backend. Matches the official Codex CLI.
const ORIGINATOR = process.env.GPTIMAGE_ORIGINATOR || "codex_cli_rs";

const INSTRUCTIONS =
  "You are an image generation assistant running inside the Codex backend. " +
  "Always satisfy the request by invoking the image_generation tool exactly once. " +
  "Do not respond with text only.";

// Parse the SSE stream and pull out the first image_generation result (base64).
async function parseImageFromSSE(stream) {
  const reader = stream.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    // SSE events are separated by a blank line.
    let sep;
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      const dataLine = rawEvent
        .split("\n")
        .filter((l) => l.startsWith("data:"))
        .map((l) => l.slice(5).trim())
        .join("");
      if (!dataLine || dataLine === "[DONE]") continue;
      let json;
      try {
        json = JSON.parse(dataLine);
      } catch {
        continue; // heartbeat / non-JSON keepalive
      }
      if (
        json.type === "response.output_item.done" &&
        json.item?.type === "image_generation_call" &&
        typeof json.item.result === "string"
      ) {
        return json.item.result;
      }
      // Surface a backend-side error event instead of hanging until stream end.
      if (json.type === "response.failed" || json.type === "error") {
        const msg = json.response?.error?.message || json.error?.message || "unknown backend error";
        throw new Error(`codex backend error: ${msg}`);
      }
    }
  }
  throw new Error("no image_generation result returned by codex backend");
}

/**
 * Generate an image.
 * @param {{access: string, accountId?: string}} creds
 * @param {{prompt: string, quality?: string, size?: string, referenceDataUrls?: string[]}} opts
 * @returns {Promise<string>} base64-encoded PNG
 */
export async function generateImage(creds, opts) {
  const userContent = [{ type: "input_text", text: opts.prompt }];
  for (const dataUrl of opts.referenceDataUrls ?? []) {
    userContent.push({ type: "input_image", image_url: dataUrl });
  }

  const tool = {
    type: "image_generation",
    output_format: "png",
    quality: opts.quality || "high",
  };
  if (opts.size && opts.size !== "auto") tool.size = opts.size;

  const body = {
    model: DEFAULT_MODEL,
    instructions: INSTRUCTIONS,
    input: [{ role: "user", content: userContent }],
    tools: [tool],
    tool_choice: { type: "image_generation" },
    stream: true,
    store: false,
  };

  const res = await fetch(CODEX_RESPONSES_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${creds.access}`,
      ...(creds.accountId ? { "chatgpt-account-id": creds.accountId } : {}),
      originator: ORIGINATOR,
      Accept: "text/event-stream",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok || !res.body) {
    const detail = await res.text().catch(() => "");
    if (res.status === 401) {
      throw new Error(`unauthorized (401) — token rejected. Re-run \`npm run login\`. ${detail.slice(0, 200)}`);
    }
    if (res.status === 429) {
      throw new Error(`rate limited (429) by your ChatGPT plan. Wait and retry. ${detail.slice(0, 200)}`);
    }
    throw new Error(`codex responses request failed: ${res.status} ${detail.slice(0, 400)}`);
  }
  return parseImageFromSSE(res.body);
}
