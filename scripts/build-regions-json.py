#!/usr/bin/env python3

import json
from pathlib import Path

FILES = [
    "regions-africa-osmfr.json",
    "regions-asia-osmfr.json",
    "regions-central-america-osmfr.json",
    "regions-europe-1-osmfr.json",
    "regions-europe-2-osmfr.json",
    "regions-europe-3-osmfr.json",
    "regions-north-america-osmfr.json",
    "regions-oceania-osmfr.json",
    "regions-russia-osmfr.json",
    "regions-south-america-osmfr.json",
]

regions_dir = Path("config/regions")
output = Path("config/regions.json")

regions = []

for filename in FILES:
    path = regions_dir / filename

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"{path} does not contain a JSON list")

    regions.extend(data)

regions.sort(key=lambda r: (r["id"], r["path"]))

with output.open("w", encoding="utf-8") as f:
    json.dump(regions, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"Generated {output}: {len(regions)} entries")
