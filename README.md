# Automation Template

This folder contains a reusable GitHub Actions workflow you can copy into other resource pack repositories to run centralized automation.

## Files

- `.github/workflows/reusable-pack-update.yml` — Reusable workflow that runs in the target repo and uses its `scripts/` and files
- `.github/workflows/auto-update.yml` — Minimal caller workflow example for pack repos

## Quick Setup (Per Pack Repo)

1. Copy the `.github/workflows` folder from `automation-template` into your target repo.
2. Ensure your repo contains:
   - `VERSION` (e.g., `1.0.0`)
   - `pack.mcmeta`
   - `assets/` folder
   - `scripts/resolve_versions.py`, `scripts/update_pack.py`, `scripts/upload_modrinth.py`
3. Edit `.github/workflows/auto-update.yml`:
   - Replace `OWNER/REPO` with your automation repo path (or leave as local call if you keep the reusable file in the same repo)
   - Set `modrinth_project_id` and `pack_name`
4. Add repo secret `MODRINTH_TOKEN` in GitHub → Settings → Secrets and variables → Actions.

## How It Works

- `auto-update.yml` calls the reusable workflow.
- The reusable workflow:
  - Resolves missing game versions via `scripts/resolve_versions.py` (using misode/mcmeta API for pack formats)
  - Updates pack files via `scripts/update_pack.py`
  - Zips `pack.mcmeta` + `assets/`
  - Uploads per pack-format group via `scripts/upload_modrinth.py`

## Local Test

You can test the resolver locally:

```bash
python3 scripts/resolve_versions.py "your-modrinth-project-id"
```

This prints a JSON with groups and versions determined by API-only data.

## Notes

- The reusable workflow assumes scripts live inside each pack repo under `scripts/`.
- If you plan to centralize scripts in another repo, adjust the workflow to checkout that repo and call scripts from there.
