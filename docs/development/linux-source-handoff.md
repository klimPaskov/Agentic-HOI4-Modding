# Linux source handoff

Prepared on branch `feat/linux-support` from source main `374443246bfb67823d2ea1214af8714d1dd80bbd`. The source commit precedes its generated manifest commit; the manifest's `generated_for_revision` identifies that exact source snapshot. Publication and the app's full disposable installation remain parent-owned.

## Contract and integrity

The single `hoi4-mod-setup.manifest.json` uses schema 5.0.0. The new `schemas/remote-manifest.v5.schema.json` adds Linux platform declarations and closed `platform_targets` / `platform_pins` health parameters. Original schema 3 and 4 files remain unchanged. Source schema loading selects only known majors and the current publication validator requires major 5. Older app versions must upgrade before using this manifest.

The shared HOI4 Agent Tools public version remains 4.0.3 with npm integrity `sha512-pgiQYcQiWsba78IOK1DzOb7feEl0ktpiZg3LdyxSMcklA7HV+Zofo3hdR5BOp9YWlWHubrTkl6AMtBgDhqnUmQ==`. Windows records 5,387 files and tree SHA-256 `b93b47b341e6bc33a0822d631e187af7e3c29eec48196ccd10c89f957729dc35`. Native Linux x86_64/glibc records 5,253 entries and tree SHA-256 `c2f7344ff1ee5ab4ba1c99299cdab2fbf01c1b56bf87d866810dfdafc9d30d41`. Both platforms' `dist/bin/stdio.js` is 4,205 bytes with SHA-256 `e503ef634bcd473b5a7225f6752ff7d99c9897cb2126dac3eb2c4cc55859f24e`.

The native npm package contains exactly two reviewed internal links: `node_modules/.bin/node-which` points to `../which/bin/node-which`; `node_modules/.bin/semver` points to `../semver/bin/semver.js`. Each link contributes bytes `symlink\0` followed by its literal UTF-8 target to the same path/length/content tree hash and counts as an entry. Every other link, an altered/missing target, an escaping target, a directory target or a target containing another link is rejected. Windows permits no package links. No package file or mutable dependency is excluded to make verification pass.

Linux installation uses `$XDG_DATA_HOME/hoi4-mod-setup/npm` or `~/.local/share/hoi4-mod-setup/npm`; set XDG paths must be bounded and absolute. Modules are under `lib/node_modules/hoi4-agent-tools`, and `bin/hoi4-agent-tools` must point exactly to `../lib/node_modules/hoi4-agent-tools/dist/bin/stdio.js`. The bootstrap discovers native Node/npm, invokes the resolved npm JavaScript entry directly, installs the exact public package without lifecycle scripts and preserves the same registry, tree, entry and local-archive checks as Windows. Linux requires native Node LTS 22 or newer beforehand and never invokes sudo. The app registers trusted absolute Node plus the verified package entry for each selected coding client, preserving shared skill/agent projections.

## Images and live workflows

GPTImage source tree `06f78000782148bc0079b659389fbd52cdc03179e1075b260bf788fb7791f8f4` and lock `bd75719d34e7a161e8b3d712fdb358ba1b89dcc6d6f6cd614ddbc38032a45778` are unchanged. Fresh native Linux installation from exact committed vendor blobs returned `ready` with empty stderr and advertised `generate_image`, `image_auth_status`, and `list_references`. Its installed SDK subtree has 677 files and SHA-256 `0b288e08420553e6e5545e42d904c3877f59bb9f02d06038bcc8f7f5979c01ff`, identical to a fresh Windows install. The source manifest pins vendor source and npm lock; the app continues to record observed installed SDK receipt evidence.

Other image routes retain package-owned adapters and existing provider declarations. The Python adapter's Linux vault reader invokes fixed `/usr/bin/secret-tool` with target `default`, service `com.klimpaskov.hoi4-mod-setup`, and the opaque credential reference as username, matching the app's Secret Service backend. It suppresses diagnostic output, bounds results and returns unavailable when the vault/helper cannot answer. Actual desktop D-Bus/Secret Service compatibility is checked by the app security owner with synthetic credentials; no real user keys or provider calls are part of source validation.

Clausewitz declares native Linux support without WSL/SSH, retaining source `97c85437081904d5ad07bae1623ec58d1c0a5b9e` and native HOI4 1.19.2 only. Manual game/server/process-read readiness remains required before registration. Windows uses WSL and macOS SSH as before. HOI4 Live Tools and the Meshy/Blender bootstrap remain Windows-verified; no Linux 3D or Live Tools route is invented. The installed Linux guide is declared as `docs.linux`, including prerequisites and manual registration shapes.

## Verification and remaining parent gates

- Windows Python 3.13 source suite: 132 tests pass with the native symlink fixture skipped; native Ubuntu 24.04 Python 3.12 source suite: all 132 tests pass, including real filesystem links.
- A fresh isolated XDG bootstrap with root-owned system Node 22.23.3/npm 10.9.9 installs and verifies the Linux tree, then initializes and advertises all 28 Agent Tools routes without invoking a tool or launching the game.
- Fresh native GPTImage CLI and tools/list checks pass without sign-in; source and lock hashes match exact committed bytes across platforms.
- Tier/effort policies and projections remain valid for 23 agents and four generated runtimes; all 57 guidance files stay below the single-read ceiling. Wiki snapshot validation passes for 54 pages and all 134 media files.
- Regression cases cover unknown schema majors, incomplete platform pins, bounded XDG paths, native npm discovery/old-Node refusal, exact Secret Service attributes, missing/unlisted/altered/escaping links and changed target bytes.

Source publication does not establish real HOI4 loading, Clausewitz game compatibility, authenticated image generation, account login, an installed Blender bridge, desktop package replacement or system updater behavior. The parent owns app schema adoption, native client retargeting, supervised-process security, full app installation transactions, native release gates and publication.
