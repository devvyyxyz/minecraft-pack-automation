import json
import sys


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "versions_to_update.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    groups = data.get("groups", [])
    for i, group in enumerate(groups):
        versions = ",".join(group.get("versions", []))
        print(f"GROUP_{i}_VERSIONS={versions}")
        print(f"GROUP_{i}_PACK_FORMAT={group.get('pack_format')}")
    print(f"TOTAL_GROUPS={len(groups)}")


if __name__ == "__main__":
    main()
