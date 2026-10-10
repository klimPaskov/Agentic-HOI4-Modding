# HOI4 Live Tools installation

HOI4 Live Tools is an MCP server that lets an agent drive a running Hearts of Iron IV on Windows: launch and load games, read the screen (date, popups, text, the top bar, tooltips, open panels, the map), run time while answering events, fire events and effects through the console, save, query the plain-text save, read the error log, and summarise the player's country.
This page belongs to the `hoi4-live-playtest` skill and covers installation, registration and troubleshooting; the skill itself describes how agents use the server.

It is separate from HOI4 Agent Tools (`hoi4_agent_tools`), which works on source files and never touches the running game.

## Requirements

- Windows 10 or 11 and Hearts of Iron IV, windowed or borderless, with the interface scale at 1.
- Python 3.9 or newer for the installer. The installer creates a private environment with `numpy`, `Pillow` and `opencv-python-headless`; nothing else is installed globally.
- The Windows OCR English language component (installed with an English Windows display language).
- Optional: `ffmpeg` on `PATH` for the fallback screen capture.
- Plain-text saves for save queries: `save_as_binary=no` in `Documents/Paradox Interactive/Hearts of Iron IV/settings.txt`. The server never edits that file; it reports binary saves instead.

## Install

**With HOI4 Mod Setup.** Select **HOI4 Live Tools** under the optional workflows. The app copies this skill into the project, then runs the package's bootstrap, which downloads the pinned release, verifies its SHA-256, installs it for the current user and registers it for your coding clients. The project readiness page shows **ready**, or **incomplete** with the reason.

**By hand.** Download `hoi4-live-tools-<version>.zip` from <https://github.com/klimPaskov/HOI4-Live-Tools/releases>, unpack it anywhere and run:

```powershell
python install.py
```

It installs to `%LOCALAPPDATA%\hoi4-live-tools` (`app\`, `venv\`, `artifacts\`, and an optional `config.json` for settings), starts the server once to confirm it lists its tools, and registers it for the user in every client it finds: Claude Code (`~/.claude.json`), Codex (`~/.codex/config.toml`, with a 1800 second tool timeout), Cursor and OpenCode. Options: `--register claude,codex` (or `all`, `none`) and `--prefix <folder>`. `python install.py status` shows what is installed and registered; running it again upgrades in place and keeps the registrations.

Then restart the client and check that the server is listed (`/mcp` in Claude Code) and that `hoi4_status` answers. Check the environment without touching the game:

```powershell
& "$env:LOCALAPPDATA\hoi4-live-tools\app\hoi4-live-tools.cmd" selftest
```

It finds the game and user folders (Steam libraries and redirected Documents folders are detected), ffmpeg and the text-save setting, and runs one OCR request.

## Register by hand

The registration lives in the user's own client configuration, not in the mod's shared files, because the install folder can differ per machine.

Claude Code:

```powershell
claude mcp add --scope user hoi4-live -- "$env:LOCALAPPDATA\hoi4-live-tools\app\hoi4-live-tools.cmd"
```

Codex (`~/.codex/config.toml`):

```toml
[mcp_servers.hoi4-live]
command = 'C:\Users\<you>\AppData\Local\hoi4-live-tools\app\hoi4-live-tools.cmd'
args = []
startup_timeout_sec = 30
tool_timeout_sec = 1800
```

Codex's default tool timeout (60 seconds) is too short for loading a save or stepping weeks of game time; keep `tool_timeout_sec`. Claude Code's default is long enough.

## How agents use it

- Live testing stays user-owned unless the user asks for it; the `hoi4-live-playtest` skill enforces that.
- All agents on one desktop share a lock (`%TEMP%\hoi4_live_desktop.lock`). A run holds it with `hoi4_lock`, and every acting tool refuses to type outside the game window.
- The server writes only `hoi4live_*` saves, never deletes anything, and changes the playset only through `hoi4_telemetry enable|disable|restore`, which backs up `dlc_load.json` first.
- `test` mode allows console commands, events and effects; `campaign` mode refuses them so that an agent plays with player-equivalent actions.

## Settings

Defaults need no file. To change something (game folder, console key, OCR language, capture method), create `%LOCALAPPDATA%\hoi4-live-tools\config.json` with only the keys to override; the launcher passes it to the server when it exists. Keys are listed in the server's README under Configuration.

## Remove

`python install.py uninstall` (from the release folder or `app\install.py`) removes the program, its environment and the registrations it wrote; `--purge` also removes `config.json` and `artifacts\`. An entry named `hoi4-live` that belongs to another program is left alone.

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| The client does not list `hoi4-live` | Restart the client. Run `python install.py status` to see the registrations; `python install.py register` writes them again. |
| `install.py` stops with exit code 3 | The installed server did not answer. Run `hoi4-live-tools.cmd selftest` from the install folder and read the first line that fails. |
| `install.py` stops with exit code 4 | The server is installed, but a client entry could not be written or a `hoi4-live` entry of another program exists. The message names the file; fix or remove that entry and run `python install.py register`. |
| The pip step fails | The machine could not reach PyPI, or a proxy blocks it. Retry on a network that allows `pip install numpy`. |
| `selftest` reports a failing OCR line | Install the English (United States) language pack with its OCR component, or set `ocr.language` in `config.json` to an installed OCR language. |
| A tool times out while loading or stepping time | Raise the client's tool timeout as shown above. |
| Save queries report binary saves | Set `save_as_binary=no` in `settings.txt` yourself and save again. |
| A tool reports the desktop lock is held | Another agent is using the game. Wait for it to release the lock; a holder that stopped refreshing it for ten minutes is treated as stale. |
| Screenshots are black | Install `ffmpeg`, or set `capture.method` to `ddagrab` in `config.json`. |
