import json
import os
import subprocess
import sys


def read_from_version_json(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return (
            data.get("version")
            or data.get("pack_version")
            or data.get("name")
        )
    except Exception:
        return None


def read_latest_tag() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return None


def main():
    # Optional first arg: explicit version override
    override = sys.argv[1] if len(sys.argv) > 1 else None
    if override:
        print(override)
        return

    # version.json
    v = read_from_version_json("version.json")
    if v:
        print(v)
        return

    # VERSION file
    if os.path.exists("VERSION"):
        with open("VERSION", "r", encoding="utf-8") as f:
            print(f.read().strip())
        return

    # Tag-based fallbacks
    ref_type = os.environ.get("GITHUB_REF_TYPE", "")
    ref_name = os.environ.get("GITHUB_REF_NAME", "")
    if ref_type == "tag" and ref_name:
        print(ref_name)
        return

    tag = read_latest_tag()
    if tag:
        print(tag)
        return

    print("", end="")


if __name__ == "__main__":
    main()
