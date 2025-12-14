#!/usr/bin/env python3
"""
pack.mcmeta Updater
Updates pack.mcmeta with version-specific pack_format and description.
"""

import json
import sys
from pathlib import Path
from typing import Optional


def update_pack_mcmeta(
    pack_mcmeta_path: str,
    minecraft_version: str,
    pack_format: int,
    base_description: Optional[str] = None
) -> bool:
    """
    Update pack.mcmeta with version-specific values.
    
    Args:
        pack_mcmeta_path: Path to pack.mcmeta file
        minecraft_version: Target Minecraft version (e.g., "1.20.1")
        pack_format: Pack format number for this version
        base_description: Base description text (optional, will preserve if not provided)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        mcmeta_file = Path(pack_mcmeta_path)
        
        if not mcmeta_file.exists():
            print(f"ERROR: pack.mcmeta not found at {pack_mcmeta_path}", file=sys.stderr)
            return False
        
        with open(mcmeta_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "pack" not in data:
            print("ERROR: Invalid pack.mcmeta structure (missing 'pack' key)", file=sys.stderr)
            return False
        
        # Update pack_format
        data["pack"]["pack_format"] = pack_format
        
        # Update description with version info
        if base_description is None:
            # Extract base description (everything before " (Auto-updated...")
            current_desc = data["pack"].get("description", "Resource Pack")
            base_description = current_desc.split(" (Auto-updated")[0].strip()
        
        data["pack"]["description"] = f"{base_description} (Auto-updated for Minecraft {minecraft_version})"
        
        # Write back with proper formatting
        with open(mcmeta_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        
        print(f"[+] Updated pack.mcmeta for Minecraft {minecraft_version}", file=sys.stderr)
        return True
    
    except json.JSONDecodeError:
        print(f"ERROR: pack.mcmeta is not valid JSON", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Failed to update pack.mcmeta: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 4:
        print(
            "Usage: python3 update_pack.py <pack.mcmeta_path> <minecraft_version> <pack_format> [base_description]",
            file=sys.stderr
        )
        sys.exit(1)
    
    pack_mcmeta_path = sys.argv[1]
    minecraft_version = sys.argv[2]
    
    try:
        pack_format = int(sys.argv[3])
    except ValueError:
        print(f"ERROR: pack_format must be an integer, got '{sys.argv[3]}'", file=sys.stderr)
        sys.exit(1)
    
    base_description = sys.argv[4] if len(sys.argv) > 4 else None
    
    success = update_pack_mcmeta(pack_mcmeta_path, minecraft_version, pack_format, base_description)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
