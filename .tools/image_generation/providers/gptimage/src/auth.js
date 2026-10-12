// Authentication for gptimage.
//
// We authenticate against ChatGPT the same way the official Codex CLI does:
// an OAuth + PKCE flow against auth.openai.com that mints a token tied to the
// user's ChatGPT subscription (NOT an API key — usage is billed to the plan).
//
// Token resolution order:
//   1. GPTIMAGE_ACCESS_TOKEN env var (escape hatch / CI)
//   2. our own store:   ~/.gptimage/auth.json   (written by `login.js`)
//   3. codex fallback:  ~/.codex/auth.json          (if you already ran codex login)
//
// When an access token is expired we refresh it in place, writing the rotated
// tokens back to whichever store they came from — so the Codex CLI keeps working
// if that's where we read them from.

import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";

export const CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann";
export const AUTHORIZE_URL = "https://auth.openai.com/oauth/authorize";
export const TOKEN_URL = "https://auth.openai.com/oauth/token";
export const REDIRECT_URI = "http://localhost:1455/auth/callback";
export const SCOPE = "openid profile email offline_access";
const JWT_CLAIM_PATH = "https://api.openai.com/auth";
const EXPIRY_MARGIN_MS = 60_000;

export const OUR_STORE = path.join(os.homedir(), ".gptimage", "auth.json");
export const CODEX_STORE = path.join(os.homedir(), ".codex", "auth.json");

// ---------------------------------------------------------------------------
// JWT helpers (decode only — we never verify signatures, the server does that)
// ---------------------------------------------------------------------------

export function decodeJwt(token) {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    return JSON.parse(Buffer.from(parts[1], "base64url").toString("utf8"));
  } catch {
    return null;
  }
}

export function accountIdFromToken(accessToken) {
  const claims = decodeJwt(accessToken);
  return claims?.[JWT_CLAIM_PATH]?.chatgpt_account_id;
}

export function planFromToken(accessToken) {
  const claims = decodeJwt(accessToken);
  return claims?.[JWT_CLAIM_PATH]?.chatgpt_plan_type;
}

// Expiry as epoch ms, read straight from the access token's `exp` claim.
function expiryFromToken(accessToken) {
  const claims = decodeJwt(accessToken);
  return typeof claims?.exp === "number" ? claims.exp * 1000 : null;
}

// ---------------------------------------------------------------------------
// Store readers — each returns a normalized record or null
//   { access, refresh, accountId, expires, store, format }
// ---------------------------------------------------------------------------

async function readJson(file) {
  try {
    return JSON.parse(await fs.readFile(file, "utf8"));
  } catch {
    return null;
  }
}

function normalizeOurFormat(data, store) {
  if (!data?.access) return null;
  return {
    access: data.access,
    refresh: data.refresh ?? null,
    accountId: data.account_id ?? accountIdFromToken(data.access) ?? null,
    expires: data.expires ?? expiryFromToken(data.access),
    store,
    format: "ours",
  };
}

function normalizeCodexFormat(data, store) {
  const t = data?.tokens;
  if (!t?.access_token) return null;
  return {
    access: t.access_token,
    refresh: t.refresh_token ?? null,
    accountId: t.account_id ?? accountIdFromToken(t.access_token) ?? null,
    expires: expiryFromToken(t.access_token),
    store,
    format: "codex",
  };
}

// ---------------------------------------------------------------------------
// Store writers — persist rotated tokens back in the source file's own format
// ---------------------------------------------------------------------------

async function writeOurStore(record) {
  await fs.mkdir(path.dirname(OUR_STORE), { recursive: true });
  const payload = {
    type: "oauth",
    access: record.access,
    refresh: record.refresh,
    account_id: record.accountId,
    expires: record.expires,
    last_refresh: new Date().toISOString(),
  };
  await fs.writeFile(OUR_STORE, JSON.stringify(payload, null, 2), { mode: 0o600 });
}

async function writeBack(record) {
  if (record.format === "codex") {
    const existing = (await readJson(CODEX_STORE)) ?? { auth_mode: "chatgpt", OPENAI_API_KEY: null, tokens: {} };
    existing.tokens = {
      ...existing.tokens,
      access_token: record.access,
      refresh_token: record.refresh,
      account_id: record.accountId,
    };
    existing.last_refresh = new Date().toISOString();
    await fs.writeFile(CODEX_STORE, JSON.stringify(existing, null, 2), { mode: 0o600 });
  } else {
    await writeOurStore(record);
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

// Read the first available credentials without refreshing.
export async function loadAuth() {
  if (process.env.GPTIMAGE_ACCESS_TOKEN) {
    const access = process.env.GPTIMAGE_ACCESS_TOKEN;
    return {
      access,
      refresh: null,
      accountId: process.env.GPTIMAGE_ACCOUNT_ID ?? accountIdFromToken(access) ?? null,
      expires: expiryFromToken(access),
      store: "env",
      format: "env",
    };
  }
  const ours = normalizeOurFormat(await readJson(OUR_STORE), OUR_STORE);
  if (ours) return ours;
  const codex = normalizeCodexFormat(await readJson(CODEX_STORE), CODEX_STORE);
  if (codex) return codex;
  return null;
}

export function isExpired(record) {
  if (!record?.expires) return false; // unknown -> assume usable, server will 401 if not
  return Date.now() >= record.expires - EXPIRY_MARGIN_MS;
}

export async function refreshTokens(refreshToken) {
  const res = await fetch(TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: refreshToken,
      client_id: CLIENT_ID,
    }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`token refresh failed: ${res.status} ${text.slice(0, 300)}`);
  }
  const json = await res.json();
  if (!json?.access_token) throw new Error("token refresh response missing access_token");
  return {
    access: json.access_token,
    refresh: json.refresh_token ?? refreshToken,
    expires: json.expires_in ? Date.now() + json.expires_in * 1000 : expiryFromToken(json.access_token),
  };
}

// Main entry point used by the server / CLI: returns a guaranteed-fresh
// { access, accountId } pair, refreshing and persisting if needed.
export async function getValidCredentials() {
  const record = await loadAuth();
  if (!record) {
    throw new Error(
      "Not authenticated. Run `npm run login` (sign in with your ChatGPT account) " +
        "or install the Codex CLI and run `codex login`.",
    );
  }
  if (!isExpired(record)) return { access: record.access, accountId: record.accountId };

  if (!record.refresh) {
    throw new Error("Access token expired and no refresh token available. Run `npm run login` again.");
  }
  const refreshed = await refreshTokens(record.refresh);
  const updated = {
    ...record,
    access: refreshed.access,
    refresh: refreshed.refresh,
    expires: refreshed.expires,
    accountId: record.accountId ?? accountIdFromToken(refreshed.access),
  };
  await writeBack(updated);
  return { access: updated.access, accountId: updated.accountId };
}

export { writeOurStore };
