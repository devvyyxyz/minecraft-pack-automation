import json
import os
import subprocess
import sys

# ANSI color codes
class Color:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'


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
        print(f"{Color.CYAN}[*] Using provided pack_version input{Color.RESET}", file=sys.stderr)
        print(override)
        return

    # version.json
    v = read_from_version_json("version.json")
    if v:
        print(f"{Color.GREEN}[+] Found version in version.json{Color.RESET}", file=sys.stderr)
        print(v)
        return

    # VERSION file
    if os.path.exists("VERSION"):
        print(f"{Color.GREEN}[+] Found VERSION file{Color.RESET}", file=sys.stderr)
        with open("VERSION", "r", encoding="utf-8") as f:
            print(f.read().strip())
        return

    # Tag-based fallbacks
    ref_type = os.environ.get("GITHUB_REF_TYPE", "")
    ref_name = os.environ.get("GITHUB_REF_NAME", "")
    if ref_type == "tag" and ref_name:
        print(f"{Color.YELLOW}[*] Using tag from GITHUB_REF_NAME{Color.RESET}", file=sys.stderr)
        print(ref_name)
        return

    tag = read_latest_tag()
    if tag:
        print(f"{Color.YELLOW}[*] Using latest git tag{Color.RESET}", file=sys.stderr)
        print(tag)
        return

    print("", end="")


if __name__ == "__main__":
    main()
