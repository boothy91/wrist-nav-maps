#!/usr/bin/env python3
"""Update regions.json PBF URLs from Geofabrik index"""
import json, urllib.request

INDEX_URL = "https://download.geofabrik.de/index-v1.json"

with urllib.request.urlopen(INDEX_URL) as r:
    index = json.load(r)

# Build lookup: id -> pbf url
lookup = {}
for f in index["features"]:
    p = f["properties"]
    lookup[p["id"]] = p["urls"]["pbf"]

with open("config/regions.json") as f:
    regions = json.load(f)

updated = 0
for region in regions:
    rid = region["id"]
    if rid in lookup:
        region["pbf"] = lookup[rid]
        updated += 1
    else:
        print(f"WARNING: {rid} not found in Geofabrik index")

with open("config/regions.json", "w") as f:
    json.dump(regions, f, indent=2)

print(f"Updated {updated}/{len(regions)} regions")
