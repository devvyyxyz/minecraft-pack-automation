# Minecraft Pack Automation

Use this repo’s reusable GitHub Actions workflow to build and publish your resource pack. Here’s what you need in your pack repository.

## What You Must Have
- VERSION — your pack’s version string (used in published version labels).
- pack.mcmeta, pack.png, and your resource pack contents under assets/.
- scripts/update_pack.py — updates pack files for the target Minecraft versions/pack formats.
- scripts/upload_modrinth.py — uploads the built zip to Modrinth; CLI: zip path, project id, comma-separated MC versions, version label, token.
- scripts/resolve_versions.py (optional but recommended) — outputs the Minecraft versions and pack formats you want published. If missing, the workflow falls back to latest + previous release.

## Workflow to Add in Your Repo
- Copy auto-update.yml from this repo’s .github/workflows/ directory into the same path in your pack repo.
- In that file, set:
  - uses: kaispife/minecraft-pack-automation/.github/workflows/reusable-pack-update.yml@main (or your fork path).
  - modrinth_project_id: your Modrinth project slug/ID.
  - pack_name: name used for the zip file.
- Provide secret MODRINTH_TOKEN via GitHub repo secrets and reference it in the secrets block (recommended for simplicity and security).
- Adjust the cron schedule to your desired cadence.

## What the Reusable Workflow Does
- Resolves target versions (prefers your scripts/resolve_versions.py; otherwise latest + previous release) and groups them by pack format.
- Runs scripts/update_pack.py to regenerate assets.
- Zips pack.mcmeta, pack.png, and assets/ into build/<pack_name>.zip.
- Calls scripts/upload_modrinth.py per pack-format group to publish versions to Modrinth.

## Notes
- Keep the CLIs of your scripts stable; the workflow calls them directly.
- If you need different packaging, edit the zip step in the reusable workflow.
