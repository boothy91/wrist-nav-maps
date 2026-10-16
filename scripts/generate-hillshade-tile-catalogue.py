#!/usr/bin/env python3
"""Generate all OSMFR hillshade HGT catalogues and a master index."""

import hashlib
import json
import math
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS_DIR = ROOT / "config/regions"
OUTPUT_DIR = REGIONS_DIR
MARGIN = 0.2

GROUPS = [
    "africa",
    "asia",
    "central-america",
    "europe-1",
    "europe-2",
    "europe-3",
    "north-america",
    "oceania",
    "russia",
    "south-america",
]

REPO = "Boothy91/wrist-nav-maps"
BRANCH = "main"


def get_polygon(region):
    url = (
        region["pbf"]
        .replace("-latest.osm.pbf", ".poly")
        .replace("extracts", "polygons", 1)
    )
    request = urllib.request.Request(
        url, headers={"User-Agent": "wrist-nav-maps-tile-catalogue/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        content = response.read().decode("utf-8")

    coords = []
    for line in content.splitlines():
        parts = line.strip().split()
        if len(parts) == 2:
            try:
                coords.append((float(parts[0]), float(parts[1])))
            except ValueError:
                pass

    if not coords:
        raise ValueError(f"No coordinates found: {url}")

    lons = [lon for lon, _ in coords]
    lats = [lat for _, lat in coords]
    raw_span = max(lons) - min(lons)
    shifted = [lon + 360 if lon < 0 else lon for lon in lons]
    shifted_span = max(shifted) - min(shifted)

    if raw_span > 180 and shifted_span < raw_span:
        east = [(lon, lat) for lon, lat in coords if lon >= 0]
        west = [(lon, lat) for lon, lat in coords if lon < 0]
        main = east if len(east) >= len(west) else west
        lons = [lon for lon, _ in main]
        lats = [lat for _, lat in main]

    west = max(min(lons) - MARGIN, -180)
    south = max(min(lats) - MARGIN, -90)
    east = min(max(lons) + MARGIN, 180)
    north = min(max(lats) + MARGIN, 90)

    tiles = []
    for lat in range(math.floor(south), math.floor(north) + 1):
        for lon in range(math.floor(west), math.floor(east) + 1):
            ns = "N" if lat >= 0 else "S"
            ew = "E" if lon >= 0 else "W"
            tiles.append(f"{ns}{abs(lat):02d}{ew}{abs(lon):03d}.hgt")

    return {
        "id": region["id"],
        "name": region["name"],
        "bbox": {
            "west": round(west, 4),
            "south": round(south, 4),
            "east": round(east, 4),
            "north": round(north, 4),
        },
        "tiles": tiles,
    }


def main():
    catalogues = []
    master_regions = []
    seen_ids = set()

    for group in GROUPS:
        source = REGIONS_DIR / f"regions-{group}-osmfr.json"
        output = OUTPUT_DIR / f"hillshade-tiles-{group}.json"

        regions = json.loads(source.read_text())
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(get_polygon, regions))

        ids = [item["id"] for item in results]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate region IDs in {source.name}")
        if set(ids) != {item["id"] for item in regions}:
            raise ValueError(f"Source/catalogue IDs differ for {group}")
        if seen_ids.intersection(ids):
            raise ValueError(f"Region IDs overlap between catalogues: {group}")
        seen_ids.update(ids)

        document = {
            "description": f"OSMFR {group} hillshade HGT tile catalogue",
            "catalogue_id": group,
            "margin_degrees": MARGIN,
            "region_count": len(results),
            "regions": results,
        }
        content = (json.dumps(document, indent=2) + "\n").encode("utf-8")
        output.write_bytes(content)

        url = (
            f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/"
            f"config/regions/{output.name}"
        )
        catalogues.append({
            "id": group,
            "file": output.name,
            "url": url,
            "sha256": hashlib.sha256(content).hexdigest(),
            "region_count": len(results),
        })

        for region in results:
            master_regions.append({
                "id": region["id"],
                "name": region["name"],
                "catalogue_id": group,
                "catalogue_file": output.name,
            })

        print(f"Wrote {output.name}: {len(results)} regions")

    index = {
        "description": "Master index for all OSMFR hillshade HGT tile catalogues",
        "schema_version": 1,
        "margin_degrees": MARGIN,
        "catalogues": catalogues,
        "region_count": len(master_regions),
        "regions": sorted(
            master_regions,
            key=lambda item: (item["name"].casefold(), item["id"]),
        ),
    }

    index_path = OUTPUT_DIR / "hillshade-tiles-index.json"
    index_path.write_text(json.dumps(index, indent=2) + "\n")

    yorkshire = next(
        (r for r in master_regions
         if r["id"] == "yorkshire_and_the_humber"),
        None,
    )
    print(f"\nWrote {index_path.name}: {len(master_regions)} regions")
    print("Yorkshire lookup:", yorkshire or "NOT FOUND")


if __name__ == "__main__":
    main()
