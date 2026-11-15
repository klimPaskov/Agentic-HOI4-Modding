# First run

From download to a working agent in a few minutes. These are the steps HOI4 Mod Setup's own fresh-install test follows on Windows and Linux, so each one has been checked.

## Before you start

You need Git and a coding client (Claude Code, Codex or another one the app lists). Two prerequisites are not installed for you:

- **Windows:** Python 3.13 from [python.org](https://www.python.org/downloads/windows/). Node.js is optional: if it is missing, the HOI4 Agent Tools bootstrap installs the LTS release with `winget`.
- **Linux:** Node.js 22 (22.19 or newer) or 24 from your package manager, so that `/usr/bin/node` is owned by a package. Ubuntu 22.04 ships Node 12, which is too old. NodeSource's `node_22.x` repository works. A Node from nvm, a tarball or a Windows install in WSL does not count, and the Node check blocks the install. Python 3 is the system `python3`. See the [Linux setup guide](linux.md).

## Install

1. Download [HOI4 Mod Setup](https://github.com/klimPaskov/HOI4-Mod-Setup/releases/latest). On Linux run `sudo apt install ./hoi4-mod-setup_<version>_amd64.deb`. If the system warns about an unknown publisher, follow the [Run anyway guide](https://github.com/klimPaskov/HOI4-Mod-Setup/blob/main/docs/RUN_ANYWAY.md).
2. On "Start a mod project", choose **Create new mod** (or import an existing Git project). Pick the assistant that helps you fill in the next screens.
3. Enter the mod name and a one-line description, then approve the project folder and descriptor path the assistant suggests.
4. Choose your coding client under "Coding environments". Leave "Install hoi4-imagegen" checked if you want generated images.
5. Accept the defaults on the workflow and credential screens. Live testing and 3D are optional and can be added later.
6. Choose Skip Git setup if the mod is not a repository yet, then review the changes and select **Install**. The app downloads the pinned kit, installs it and runs the HOI4 Agent Tools bootstrap and health check. This takes about one to two minutes.
7. "Project ready" means the instructions, skills, wiki and MCP registrations are in place and the HOI4 Agent Tools server answered its health check.

## Check that your agent works

1. Open the mod folder in your coding client and approve the project MCP server when it asks.
2. In Claude Code, run `/mcp`. `hoi4_agent_tools` should show as connected.
3. Ask: "Use hoi4_mod_index on this mod." The agent should return an index of your mod without errors.
4. Then describe what you want to build, for example "Add a focus tree for my country".

If a step fails, run **Manage installation** in the app, then **Update and repair**, and reconnect the client. Problems and ideas go to the [issue tracker](https://github.com/klimPaskov/Agentic-HOI4-Modding/issues).
