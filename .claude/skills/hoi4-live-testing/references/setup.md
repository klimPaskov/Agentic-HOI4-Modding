# HOI4 Live Tools integration

HOI4 Live Tools is an optional MCP server that lets an agent drive a running Hearts of Iron IV on Windows: launch and load games, read the screen (date, popups, text, the top bar, tooltips, open panels, the map), run time while answering events, fire events and effects through the console, save, query the plain-text save, read the error log, and summarise the player's country.
This page belongs to the `hoi4-live-testing` skill and covers installation, registration, and troubleshooting; the skill itself describes how agents use the server.

It is separate from HOI4 Agent Tools (`hoi4_agent_tools`), which works on source files and never touches the running game.

## Requirements

- Windows 10 or 11 and Hearts of Iron IV, windowed or borderless, with the interface scale at 1.
- Python 3.9 or newer with `numpy`, `Pillow`, `scipy`, and `opencv-python`.
- The Windows OCR English language component (installed with an English Windows display language).
- Optional: `ffmpeg` on `PATH` for the fallback screen capture.
- Plain-text saves for save queries: `save_as_binary=no` in `Documents/Paradox Interactive/Hearts of Iron IV/settings.txt`. The server never edits that file; it reports binary saves instead.

## Install

1. Put the HOI4 Live Tools folder anywhere on the machine, for example `Documents\Projects\hoi4-live-tools`. The folder contains `hoi4-live-tools.cmd`.
2. Point the launcher at your Python by setting the user environment variable `HOI4_LIVE_PYTHON` to the full path of `python.exe`.
3. Check the environment without touching the game:

   ```powershell
   & "<install folder>\hoi4-live-tools.cmd" selftest
   ```

   It finds the game and user folders (Steam libraries and redirected Documents folders are detected), ffmpeg, and runs one OCR request.
4. Adjust `config.json` in the install folder only when detection fails; paths default to `auto`.

## Register the server

The install folder differs per machine, so register the server in your user-level client settings, not in the mod's shared files.

Claude Code:

```powershell
claude mcp add --scope user hoi4-live -- "<install folder>\hoi4-live-tools.cmd"
```

Loading a save or running weeks of game time takes minutes. Set a long tool timeout for Claude Code, for example the user environment variable `MCP_TOOL_TIMEOUT=1800000` (milliseconds).

Codex (`~/.codex/config.toml`):

```toml
[mcp_servers.hoi4-live]
command = '<install folder>\hoi4-live-tools.cmd'
args = []
startup_timeout_sec = 30
tool_timeout_sec = 1800
```

Restart the client, then confirm the server is listed (`/mcp` in Claude Code) and that `hoi4_status` answers.

## How agents use it

- Live testing stays user-owned unless the user asks for it; the `hoi4-live-testing` skill enforces that.
- All agents on one desktop share a lock (`%TEMP%\hoi4_live_desktop.lock`). A run holds it with `hoi4_lock`, and every acting tool refuses to type outside the game window.
- The server writes only `hoi4live_*` saves, never deletes anything, and changes the playset only through `hoi4_telemetry enable|disable|restore`, which backs up `dlc_load.json` first.
- `test` mode allows console commands, events, and effects; `campaign` mode refuses them so that an agent plays with player-equivalent actions.

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| The client does not list `hoi4-live` | The registration points at a wrong path or the client was not restarted. Run the `selftest` command with the same path, then restart the client. |
| `selftest` cannot start Python | `HOI4_LIVE_PYTHON` is unset or points at a missing interpreter. Set it to a Python 3.9+ `python.exe` that has the four packages installed. |
| OCR fails | Install the English (United States) language pack with its OCR component, or set `ocr.language` in `config.json` to an installed OCR language. |
| A tool times out while loading or stepping time | Raise the client's tool timeout as shown above. |
| Save queries report binary saves | Set `save_as_binary=no` in `settings.txt` yourself and save again. |
| A tool reports the desktop lock is held | Another agent is using the game. Wait for it to release the lock; a holder that stopped refreshing it for ten minutes is treated as stale. |
| Screenshots are black | Let the fallback capture work by installing `ffmpeg`, or set `capture.method` to `ddagrab` in `config.json`. |
