"""Canonical live-testing providers and shared component declarations."""
from __future__ import annotations
from copy import deepcopy
ALL_CLIENTS = ["claude_code", "codex", "cursor", "qoder", "opencode"]
CLAUSEWITZ_REVISION = "97c85437081904d5ad07bae1623ec58d1c0a5b9e"

def build_live_testing_table(source_root=None):
    def row(id, name, description, requirements, platforms, experimental, kind, server, component, repository, revision, guidance, version, author, license):
        url = "https://github.com/" + repository if repository else "https://klimpaskov.github.io/Agentic-HOI4-Modding/"
        return dict(id=id, display_name=name, description=description, requirements=requirements,
            documentation_url=url, supported_platforms=platforms, supported_coding_environments=ALL_CLIENTS.copy(),
            experimental=experimental, route=dict(kind=kind, server_id=server, component_id=component,
            source_repository=repository, source_revision=revision), guidance=guidance,
            supported_game_version=version, attribution=dict(author=author, url=url, license=license,
            license_url=url + "/blob/" + (revision or "main") + "/LICENSE" if repository else None))
    return dict(default_provider="clausewitz_mcp", providers=[
        row("clausewitz_mcp", "Clausewitz MCP", "Direct state reads from native Linux Hearts of Iron IV 1.19.2.",
            ["Linux native HOI4 1.19.2 only", "Manual Linux, game and Clausewitz server setup", "Native Linux host, Windows WSL or macOS SSH to Linux", "Confirm the Linux game and server are ready in HOI4 Mod Setup before registration"],
            ["windows", "macos", "linux"], False, "external_stdio", "clausewitz_linux", "workflow.live_testing",
            "smerss/Clausewitz-MCP", CLAUSEWITZ_REVISION,
            ["Use the connected clausewitz_linux server and its advertised tool list with qualified tool names.",
             "Only Linux native HOI4 1.19.2 is supported; Linux connects directly, Windows uses WSL and macOS uses SSH to Linux.",
             "Complete manual Linux/game/server setup and confirm the Linux game and server are ready in HOI4 Mod Setup before registration.",
             "Read state directly from the game process; OCR and saving are not needed for these reads.",
             "Check advertised capabilities before attempting actions; do not assume HOI4 Live Tools operation parity.",
             "Clausewitz MCP by smerss is MIT licensed: https://github.com/smerss/Clausewitz-MCP."] ,
            "1.19.2", "smerss", "MIT"),
        row("hoi4_live_tools", "HOI4 Live Tools (experimental)", "Windows game interface, console, log and save tools; slower and not thoroughly tested.",
            ["Windows", "Python 3.9 or newer", "Installed Hearts of Iron IV"], ["windows"], True,
            "local_install", "hoi4-live", "workflow.live_tools", "klimPaskov/HOI4-Live-Tools", "v1.1.0",
            ["Use the connected hoi4-live server and its advertised tools with qualified tool names.",
             "Windows is the verified platform; upstream macOS support is incomplete.",
             "This provider is experimental, slower and not thoroughly tested.",
             "Follow references/hoi4-live-tools.md for provider-specific operations and setup."],
            "Not pinned; verify against your installed game", "klimPaskov", "Apache-2.0"),
        row("none", "None", "Run the requested checks yourself and report observations.", [],
            ["windows", "macos", "linux"], False, "manual", None, None, None, None,
            ["Live testing is manual. Ask the user to run checks and supply observations.",
             "Do not launch the game or automatically fall back to desktop control."],
            "User managed", "klimPaskov", "Apache-2.0")])

def build_live_testing_components(components):
    by_id={c["id"]:deepcopy(c) for c in components}
    live=by_id["workflow.live_tools"]
    common=deepcopy(live)
    common.update(id="workflow.live_testing", display_name="Live testing guidance", description="Provider-neutral live playtest workflow and common references.", platforms=["windows", "macos", "linux"], dependencies=["core.skills"], validation=[], capabilities=["provider-neutral live testing"], notes=[], conflicts=["existing live-playtest skill with the same path"])
    common.pop("required_tools", None)
    common["source"]["include"]=["hoi4-live-playtest/**"]
    common["source"]["exclude"]=["**/.DS_Store", "hoi4-live-playtest/references/hoi4-live-tools.md"]
    live["description"]="Install the experimental Windows HOI4 Live Tools runtime; project client registrations are managed by HOI4 Mod Setup."
    live["dependencies"]=["workflow.live_testing", "mcp.hoi4_live.bootstrap"]
    live["source"]["include"]=["hoi4-live-playtest/references/hoi4-live-tools.md"]
    live["notes"]=["Windows verified only; upstream macOS support is incomplete. Experimental, slower and not thoroughly tested."]
    parameters=live["validation"][0]["parameters"]
    parameters["arguments"]=["--quiet", "--register", "none"]
    parameters["expected_writes"]=["%LOCALAPPDATA%/hoi4-live-tools/**"]
    parameters["rollback_boundary"]="Managed project registrations roll back transactionally. The per-user runtime and Python environment are external state; the bootstrap does not register global clients with --register none."
    codex=by_id["runtime.codex.live_tools_skill"]
    codex["platforms"]=["windows", "macos", "linux"]
    codex["dependencies"]=["runtime.codex.skills", "workflow.live_testing"]
    return [common, live, codex]
