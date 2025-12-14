# Minecraft Pack Automation

A reusable GitHub Actions workflow that pack repositories can call to update and publish resource packs for the **latest** and **previous** Minecraft releases.

## What It Does
- Looks up the newest and prior Minecraft release from Mojang's version manifest.
- Reads their resource pack formats and groups versions by pack_format.
- Calls your repo's `scripts/update_pack.py` to regenerate the pack contents.
- Zips `pack.mcmeta` and `assets/`, then uploads per pack-format group via your `scripts/upload_modrinth.py`.

## Use From a Pack Repo
1. Add a workflow in your pack repository that calls this reusable one, for example:

    ```yaml
    name: Auto-Update Minecraft Resource Pack

    on:
       schedule:
          - cron: '0 3 * * *'  # Daily at 3 AM UTC
       workflow_dispatch:

    jobs:
       update-pack:
          uses: devvyyxyz/minecraft-pack-automation/.github/workflows/reusable-pack-update.yml@main
          with:
             modrinth_project_id: 'your-modrinth-project-id'
             pack_name: 'Your Pack Name'
          secrets:
             MODRINTH_TOKEN: ${{ secrets.MODRINTH_API_TOKEN }}
    ```

    - Adjust the cron as needed. The secret name can differ; map it to `MODRINTH_TOKEN` in the `secrets` block.

2. Ensure your pack repo contains:
   - VERSION (your release number)
   - pack.mcmeta
   - assets/
   - scripts/update_pack.py (updates files for the target pack formats)
   - scripts/upload_modrinth.py (zip path, project id, comma-separated MC versions, version label, token)
3. Adjust the schedule in your caller workflow if you want a cadence other than daily.

## Workflow Steps
- Resolve versions: Fetch Mojang's manifest, pick latest and previous releases, read their pack formats, and write versions_to_update.json grouped by pack_format.
- Update pack: Run scripts/update_pack.py in the pack repo workspace.
- Package: Zip pack.mcmeta and assets/ into build/<pack_name>.zip.
- Publish: For each pack-format group, run scripts/upload_modrinth.py with the matched MC versions and version label <VERSION>-pf<pack_format>.

## Notes
- The workflow relies on the pack repository's scripts/update_pack.py and scripts/upload_modrinth.py; keep their CLIs stable.
- If you need different packaging rules, tweak the zip command in the reusable workflow (or open a PR here).
