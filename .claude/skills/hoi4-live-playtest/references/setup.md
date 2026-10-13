# Live-testing provider setup

Choose Clausewitz MCP (default), experimental HOI4 Live Tools, or manual testing in HOI4 Mod Setup. The app installs common playtest guidance and writes the selected route to project instructions and skills for the coding environments you select.

Clausewitz MCP requires manual Linux, native HOI4 1.19.2 and server setup. Linux connects directly; Windows connects through WSL; macOS connects through SSH to Linux. Confirm the Linux game and server are ready in HOI4 Mod Setup before registration. See [Clausewitz setup and acknowledgement](clausewitz-mcp.md).

HOI4 Live Tools is Windows verified only; macOS upstream support is incomplete. It is experimental, slower and not thoroughly tested. The app runs its pinned bootstrap with `--quiet --register none` and manages project registrations for selected clients. Manual installation may use `python .tools/mcp/bootstrap_hoi4_live_tools.py` (automatic user-client registration remains the default); use `--register none` to install the runtime without client registration. See [provider-specific setup](hoi4-live-tools.md).

Manual testing registers no server. Give the user a test recipe and record supplied observations.

For update or repair, reselect the live-testing provider and coding environments, review managed guidance and project registrations, and preserve custom project rules. Provider selection does not establish that an external Linux host is ready. Check the connected server tool list after reconnecting.
