import json
import sys

# ANSI color codes
class Color:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    RESET = '\033[0m'


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "versions_to_update.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    groups = data.get("groups", [])
    print(f"{Color.CYAN}[*] Extracting {len(groups)} pack format groups{Color.RESET}", file=sys.stderr)
    for i, group in enumerate(groups):
        versions = ",".join(group.get("versions", []))
        pf = group.get('pack_format')
        print(f"GROUP_{i}_VERSIONS={versions}")
        print(f"GROUP_{i}_PACK_FORMAT={pf}")
        print(f"{Color.GREEN}  [+] Group {i}: PF{pf} with {len(group.get('versions', []))} versions{Color.RESET}", file=sys.stderr)
    print(f"TOTAL_GROUPS={len(groups)}")


if __name__ == "__main__":
    main()
