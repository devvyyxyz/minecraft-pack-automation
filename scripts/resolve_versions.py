#!/usr/bin/env python3
"""
Minecraft Version Resolver
Fetches Minecraft releases and Modrinth versions to identify missing uploads.
Uses misode/mcmeta API for accurate, auto-updating pack format data.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass

# ANSI color codes
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


@dataclass
class MinecraftVersion:
    """Represents a Minecraft release version."""
    version: str
    pack_format: int


@dataclass
class MinecraftVersion:
    """Represents a Minecraft release version."""
    version: str
    pack_format: int


def get_pack_version() -> str:
    """Resolve pack version from environment or files.

    Priority:
    1. PACK_VERSION environment variable (set by workflow)
    2. VERSION file in current working directory (caller repo)
    3. VERSION file next to automation scripts (for local runs)
    """
    # 1. Environment variable provided by workflow
    env_ver = os.environ.get("PACK_VERSION")
    if env_ver:
        return env_ver.strip()

    # 2. Caller repo VERSION
    cwd_version = Path("VERSION")
    if cwd_version.exists():
        try:
            return cwd_version.read_text().strip()
        except Exception as e:
            print(f"ERROR: Failed to read caller VERSION file: {e}", file=sys.stderr)
            sys.exit(1)

    # 3. Automation repo VERSION (local/dev fallback)
    automation_version = Path(__file__).parent.parent / "VERSION"
    if automation_version.exists():
        try:
            return automation_version.read_text().strip()
        except Exception as e:
            print(f"ERROR: Failed to read automation VERSION file: {e}", file=sys.stderr)
            sys.exit(1)

    print("ERROR: VERSION not found. Provide PACK_VERSION env or a VERSION file.", file=sys.stderr)
    sys.exit(1)


def fetch_minecraft_releases() -> List[MinecraftVersion]:
    """
    Fetch all Minecraft Java release versions with pack formats from misode/mcmeta API.
    This API is automatically updated and includes accurate resource pack format data.
    
    Returns:
        List of MinecraftVersion objects for release versions only.
    """
    try:
        # Fetch comprehensive version data from misode/mcmeta (community-maintained, auto-updated)
        url = "https://raw.githubusercontent.com/misode/mcmeta/summary/versions/data.json"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'XYZ-Classic-Panorama-Updater/1.0')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            versions_data = json.loads(response.read().decode())
        
        releases = []
        skipped = []
        
        for version_obj in versions_data:
            # Only process release versions (skip snapshots, pre-releases, etc.)
            if version_obj.get("type") != "release":
                continue
            
            version_str = version_obj.get("id")
            resource_pack_version = version_obj.get("resource_pack_version")
            
            if version_str and resource_pack_version is not None:
                releases.append(MinecraftVersion(version=version_str, pack_format=resource_pack_version))
            else:
                skipped.append(version_str)
        
        if skipped:
            print(f"[!] Skipped {len(skipped)} versions without pack_format data: {', '.join(skipped[:5])}{'...' if len(skipped) > 5 else ''}", file=sys.stderr)
        
        print(f"[+] Found {len(releases)} Minecraft release versions with resource pack formats", file=sys.stderr)
        return releases
    
    except Exception as e:
        print(f"ERROR: Failed to fetch Minecraft releases from misode/mcmeta API: {e}", file=sys.stderr)
        print(f"ERROR: This API is required for accurate pack format data.", file=sys.stderr)
        print(f"ERROR: Check your internet connection or try again later.", file=sys.stderr)
        sys.exit(1)


def resolve_modrinth_project_id(project_id_or_slug: str) -> Optional[str]:
    """Resolve a Modrinth project ID from a slug or ID.

    Tries `GET /v2/project/{id_or_slug}`. Returns None if not found (first upload).
    Returns the canonical UUID `id` if found.
    """
    try:
        url = f"https://api.modrinth.com/v2/project/{project_id_or_slug}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        pid = data.get("id") or data.get("project_id")
        if not pid:
            print(f"WARNING: Unable to resolve Modrinth project id from '{project_id_or_slug}'", file=sys.stderr)
            return None
        return pid
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"{Color.YELLOW}[!] Project '{project_id_or_slug}' not found on Modrinth (possibly first upload){Color.RESET}", file=sys.stderr)
            return None
        print(f"{Color.RED}ERROR: Modrinth API error while resolving project: {e}{Color.RESET}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to resolve Modrinth project id: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_modrinth_versions(project_id_or_slug: str) -> dict:
    """
    Fetch all versions currently uploaded to Modrinth.
    
    Args:
        project_id: Modrinth project ID (slug or UUID)
    
    Returns:
        Dict with:
        - 'game_versions': Set of Minecraft versions (e.g., {"1.20.1", "1.21"})
        - 'pack_versions': Dict mapping pack version to game versions
          (e.g., {"1.0.0": ["1.20", "1.20.1"], "1.1.0": ["1.21"]})
    """
    try:
        # Resolve to canonical project id first (supports slug or id)
        canonical_id = resolve_modrinth_project_id(project_id_or_slug)
        
        # If project doesn't exist yet (first upload), return empty sets
        if canonical_id is None:
            print(f"{Color.CYAN}[+] No existing versions on Modrinth - all pack formats will be uploaded{Color.RESET}", file=sys.stderr)
            return {'game_versions': set(), 'pack_versions': {}}
        
        url = f"https://api.modrinth.com/v2/project/{canonical_id}/versions"
        with urllib.request.urlopen(url, timeout=10) as response:
            versions = json.loads(response.read().decode())
        
        # Extract all unique game_versions and pack versions
        game_versions = set()
        pack_versions = {}
        
        for version in versions:
            version_number = version.get('version_number', '')
            game_vers = version.get('game_versions', [])
            
            game_versions.update(game_vers)
            
            if version_number:
                if version_number not in pack_versions:
                    pack_versions[version_number] = []
                pack_versions[version_number].extend(game_vers)
        
        return {
            'game_versions': game_versions,
            'pack_versions': pack_versions
        }
    
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"ERROR: Versions endpoint returned 404 for project '{project_id_or_slug}'.", file=sys.stderr)
            sys.exit(1)
        print(f"ERROR: Modrinth API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to fetch Modrinth versions: {e}", file=sys.stderr)
        sys.exit(1)


def find_missing_versions(
    minecraft_releases: List[MinecraftVersion],
    modrinth_versions: Set[str]
) -> List[MinecraftVersion]:
    """
    Identify Minecraft versions not yet uploaded to Modrinth.
    
    Args:
        minecraft_releases: All available Minecraft releases
        modrinth_versions: Versions already on Modrinth
    
    Returns:
        List of versions to upload
    """
    missing = [
        release for release in minecraft_releases
        if release.version not in modrinth_versions
    ]
    
    return missing


def group_by_pack_format(
    minecraft_releases: List[MinecraftVersion],
    modrinth_data: dict,
    pack_version: str
) -> dict:
    """
    Group Minecraft versions by pack_format and identify which groups need uploading.
    
    Args:
        minecraft_releases: All available Minecraft releases
        modrinth_data: Dict with 'game_versions' set and 'pack_versions' dict from Modrinth
        pack_version: Current pack version from VERSION file (e.g., "1.0.0")
    
    Returns:
        Dict with pack_format groups, each containing version info and upload status
    """
    modrinth_game_versions = modrinth_data['game_versions']
    modrinth_pack_versions = modrinth_data['pack_versions']
    
    # Group all versions by pack_format
    format_groups = {}
    for release in minecraft_releases:
        pf = release.pack_format
        if pf not in format_groups:
            format_groups[pf] = {
                "pack_format": pf,
                "all_versions": [],
                "missing_versions": [],
                "needs_upload": False
            }
        
        format_groups[pf]["all_versions"].append(release.version)
        
        # Check if this specific Minecraft version is missing
        if release.version not in modrinth_game_versions:
            format_groups[pf]["missing_versions"].append(release.version)
    
    # For each group, determine version range and check if pack version exists
    for pf, group in format_groups.items():
        versions = group["all_versions"]
        
        # Sort versions (simple string sort works for most cases)
        versions.sort()
        
        # Create version range string
        if len(versions) == 1:
            version_range = versions[0]
        else:
            version_range = f"{versions[0]}-{versions[-1]}"
        
        group["version_range"] = version_range
        group["version_number"] = f"{pack_version}-pf{pf}"  # e.g., "1.0.0-pf12"
        group["display_name"] = f"Pack Format {pf} ({version_range})"
        
        # Check if this pack version already exists on Modrinth for this pack_format
        # We need to upload if:
        # 1. There are missing Minecraft versions, OR
        # 2. This specific pack version doesn't exist on Modrinth
        version_number = f"{pack_version}-pf{pf}"
        existing_game_versions = modrinth_pack_versions.get(version_number, [])
        
        # Determine if we need to upload
        if version_number not in modrinth_pack_versions:
            # This pack version doesn't exist at all on Modrinth
            group["needs_upload"] = True
            group["upload_reason"] = f"Pack version {pack_version} not on Modrinth for PF{pf}"
        elif group["missing_versions"]:
            # There are new Minecraft versions not covered
            group["needs_upload"] = True
            group["upload_reason"] = f"New Minecraft versions: {', '.join(group['missing_versions'][:3])}{'...' if len(group['missing_versions']) > 3 else ''}"
        elif set(existing_game_versions) != set(versions):
            # Pack version exists but doesn't cover all expected game versions
            group["needs_upload"] = True
            group["upload_reason"] = "Game version list mismatch"
        else:
            # Already up-to-date
            group["needs_upload"] = False
            group["upload_reason"] = "Up-to-date"
    
    return format_groups


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 resolve_versions.py <modrinth_project_id>", file=sys.stderr)
        sys.exit(1)
    
    project_id = sys.argv[1]
    
    # Get pack version from VERSION file
    pack_version = get_pack_version()
    print(f"{Color.CYAN}[*] Pack version: {Color.BOLD}{pack_version}{Color.RESET}", file=sys.stderr)
    
    print(f"{Color.BLUE}[*] Fetching Minecraft releases...{Color.RESET}", file=sys.stderr)
    mc_releases = fetch_minecraft_releases()
    print(f"{Color.GREEN}[+] Found {len(mc_releases)} Minecraft release versions{Color.RESET}", file=sys.stderr)
    
    print(f"{Color.BLUE}[*] Fetching Modrinth versions for project '{project_id}'...{Color.RESET}", file=sys.stderr)
    modrinth_data = fetch_modrinth_versions(project_id)
    print(f"{Color.GREEN}[+] Found {len(modrinth_data['game_versions'])} game versions on Modrinth{Color.RESET}", file=sys.stderr)
    print(f"{Color.GREEN}[+] Found {len(modrinth_data['pack_versions'])} pack versions on Modrinth{Color.RESET}", file=sys.stderr)
    
    # Group by pack_format
    format_groups = group_by_pack_format(mc_releases, modrinth_data, pack_version)
    
    # Filter to only groups that need uploading
    groups_to_upload = {
        pf: group for pf, group in format_groups.items()
        if group["needs_upload"]
    }
    
    if groups_to_upload:
        print(f"{Color.YELLOW}[!] Found {len(groups_to_upload)} pack format groups to upload:{Color.RESET}", file=sys.stderr)
        for pf, group in sorted(groups_to_upload.items(), reverse=True):
            print(f"    {Color.CYAN}- Pack Format {pf}: {group['upload_reason']} ({group['version_range']}){Color.RESET}", file=sys.stderr)
    else:
        print(f"{Color.GREEN}[+] All pack formats are up-to-date!{Color.RESET}", file=sys.stderr)
    
    # Output JSON for workflow
    output = {
        "pack_version": pack_version,
        "groups": [
            group for group in format_groups.values()
            if group["needs_upload"]
        ],
        "all_groups": list(format_groups.values()),
        "modrinth_game_versions": sorted(list(modrinth_data['game_versions'])),
        "modrinth_pack_versions": list(modrinth_data['pack_versions'].keys()),
    }
    
    print(json.dumps(output))


if __name__ == "__main__":
    main()
