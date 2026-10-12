# GPTImage source pin

This provider ships the GPTImage MCP source from [Connected-Mate/gptimage](https://github.com/Connected-Mate/gptimage), upstream commit `49273481195c9795a4b6dc47b28549139c977025`, package version `0.1.0`, under the included MIT license.

The vendored copy includes the maintainer's Windows browser-launch fix for sign-in URLs containing `&`, a refreshed dependency lock, and a trimmed empty trailing banner line. HOI4 Mod Setup runs the MCP server directly from this project package; it does not run the upstream installer or register it globally.

GPTImage uses an undocumented ChatGPT service route. It is separate from the public OpenAI Images API and remains subject to the account's plan limits and current service behavior.
