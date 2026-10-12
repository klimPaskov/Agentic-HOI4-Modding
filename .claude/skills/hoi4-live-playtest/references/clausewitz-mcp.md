# Clausewitz MCP

[Clausewitz MCP](https://github.com/smerss/Clausewitz-MCP) by **smerss** is [MIT licensed](https://github.com/smerss/Clausewitz-MCP/blob/97c85437081904d5ad07bae1623ec58d1c0a5b9e/LICENSE). Reviewed source revision: `97c85437081904d5ad07bae1623ec58d1c0a5b9e`.

Supports **Linux native Hearts of Iron IV 1.19.2 only**. Windows uses WSL and macOS uses SSH to a Linux host. Follow the upstream documentation for manual Linux, native game, and server setup. Confirm the Linux game and server are ready in HOI4 Mod Setup before it registers the external stdio route as `clausewitz_linux`; selecting the provider alone does not install or prepare Linux.

Read state directly from the game process. These reads need no OCR or save. Inspect the connected server's tool list and use qualified names. Capability parity with HOI4 Live Tools is not promised; unsupported actions must be reported or performed manually by the user.
