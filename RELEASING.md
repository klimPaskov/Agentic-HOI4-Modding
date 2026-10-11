# Releasing Agentic HOI4 Modding

Release from the Claude-first source repository. Keep package code, generated runtime files, MCP pins, schema, and manifest evidence together. Never package machine-local credentials or generated provider outputs.

## Prepare and validate

1. Finalize the HOI4 Agent Tools 4.0.0 public package pin before choosing the release revision. The current bootstrap carries temporary local cutover evidence, so public installation must wait for npm publication and a clean published-package integrity/tree refresh using `scripts/refresh_mcp_package_pin.py`. Re-read the bootstrap, manifest, and integration guide; the bootstrap contract tests must agree on the exact version, integrity, entry hash, and package-tree evidence. Do not reuse the local archive integrity as published npm evidence.
2. Resolve the missing package license and verify redistribution permissions for the offline wiki and inherited visual assets, including the Super Events lineage. Update manifest license/provenance evidence only when supported by actual declarations. Do not infer permission from a public download.
3. Generate runtime projections and run all source checks with Python 3.13:

   ```powershell
   python -m pip install "jsonschema==4.25.1" "Pillow==12.2.0" "openpyxl==3.1.5"
   python .tools/sync/sync_agents.py
   python .tools/sync/sync_instructions.py
   python .tools/sync/sync_skills.py
   python -m unittest discover -s scripts -p "test_*.py"
   python scripts/test_agent_sync_contract.py
   python -m unittest discover -s .claude/skills/hoi4-feature-assets/tools/tests -p "test_*.py"
   python -m unittest discover -s .claude/skills/xlsx/tests -p "test_*.py"
   python .tools/sync/sync_agents.py --check
   python .tools/sync/sync_instructions.py --check
   python .tools/sync/sync_skills.py --check
   python .tools/sync/check_guidance_size.py
   python .tools/wiki/verify_wiki_snapshot.py
   python -m compileall -q .tools/3d_pipeline
   python -m unittest discover -s .tools/3d_pipeline/tests -p "test_*.py"
   python .tools/3d_pipeline/verify_environment.py
   python scripts/check_release_package.py
   git diff --check
   ```

4. Run the Blender integration script with an installed supported Blender executable: `blender --background --python-exit-code 1 --python .tools/3d_pipeline/tests/blender_rigid_weapon_attachment_integration.py`. This writes temporary fixtures only. If Blender is unavailable, record that limitation; source checks cannot establish Blender runtime behavior. Live Meshy probes require credentials and are separate from release unit tests.
5. Commit source changes, then generate the manifest against that exact source commit:

   ```powershell
   $releaseRevision = git rev-parse HEAD
   python scripts/generate_manifest_evidence.py --manifest hoi4-mod-setup.manifest.json --source-root . --revision $releaseRevision
   python scripts/validate_published_manifests.py
   git diff --check
   git add -- hoi4-mod-setup.manifest.json
   git commit -m "Refresh release manifest evidence"
   ```

   Every maintainer commit for this preparation must end with a blank line and `Co-Authored-By: Codex (gpt-6.1-sol) <noreply@openai.com>`. Add that trailer to the commit command above. The manifest commit points to its preceding source commit; it cannot hash itself.

## Push and merge

These are maintainer actions after local preparation is reviewed:

1. Push `claude-first-workflow` to origin and open a pull request targeting `main`. Review the complete branch diff and require the manifest, bootstrap, runtime, size, and release-link checks to pass.
2. Merge the pull request. The **Publish HOI4 Mod Setup manifest** workflow runs on source changes to `main`, computes exact Git blob evidence for the merged revision, and commits only `hoi4-mod-setup.manifest.json`. It guards against an advancing `main` and avoids a loop for manifest-only commits.
3. Confirm the bot manifest commit landed and the **Validate HOI4 Mod Setup manifests** workflow passed. If branch protection blocks the bot push, permit the intended workflow through the repository's reviewed protection policy or generate and merge the manifest through a separate reviewed PR. Do not disable protections indiscriminately.
4. Test HOI4 Mod Setup against the new remote manifest: select Claude Code and each compatibility runtime, inspect the install preview, install into a disposable mod, then check update/repair and both MCP registrations. No setup-app changes are assumed by this package release.

## GitHub Pages

In repository Settings ? Pages, choose **GitHub Actions** as the build source. The **Deploy documentation to GitHub Pages** workflow builds `docs/site/` with Jekyll and deploys on matching pushes to `main`; use its manual dispatch if needed. Confirm the environment URL, mobile layout, install instructions, catalog links, and screenshot links. The intended URL is `https://klimpaskov.github.io/Agentic-HOI4-Modding/`.

## Release archive and media

Choose a version tag after the generated manifest passes. Create the release from the manifest commit and attach `Agentic-HOI4-Modding.zip`. Build the ZIP from tracked files at that tag (for example `git archive --format=zip --output=Agentic-HOI4-Modding.zip <tag>`), including hidden runtime directories. Do not zip an entire working directory with caches, credentials, or untracked files. Test manual installation from the ZIP.

Upload the existing videos as GitHub release assets with these exact names:

| Asset | Maintainer source |
| --- | --- |
| `setup_app_tutorial.mp4` | Existing rendered setup-app tutorial in the maintainer's video output folder |
| `hoi4_agent_tools_promo.mp4` | Existing rendered Agent Tools promo in the maintainer's promo folder |

README and Pages use `releases/latest/download/<asset>` links. Upload both files to the same current release, verify playback/downloads, and remove the queued-upload wording after they are available. Keep MP4s outside Git. Screenshot links point to the setup app's tracked `docs/screenshots/` collection; verify that collection is present on its public `main` branch.

## Existing mod checkouts

The older OneDrive mod checkout is stale and must be updated separately after this package is released. Back up and commit local work, then use HOI4 Mod Setup update/repair to migrate from Codex-first instructions and Agent Tools 3.9.0. Preserve custom project rules during instruction merges, generate Claude-based runtime projections, reinstall the manifest-pinned MCPs, and reconnect clients. Keep the preparation worktree and the old mod checkout separate until their local changes are reconciled.
