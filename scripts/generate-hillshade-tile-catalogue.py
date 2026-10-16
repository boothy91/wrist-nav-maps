#!/usr/bin/env python3
"""Generate the OSMFR Europe 3 hillshade HGT tile catalogue."""

import json
import math
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS_FILE = ROOT / "config/regions/regions-europe-3-osmfr.json"
OUTPUT_FILE = ROOT / "config/regions/hillshade-tiles-europe-3.json"
MARGIN = 0.2


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

    # Match the existing hillshade workflow's antimeridian handling.
    if raw_span > 180 and shifted_span < raw_span:
        east = [(lon, lat) for lon, lat in coords if lon >= 0]
        west = [(lon, lat) for lon, lat in coords if lon < 0]
        main = east if len(east) >= len(west) else west
        lons = [point[0] for point in main]
        lats = [point[1] for point in main]

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
    regions = json.loads(REGIONS_FILE.read_text())
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(get_polygon, regions))

    ids = [item["id"] for item in results]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate region IDs detected")
    if set(ids) != {item["id"] for item in regions}:
        raise ValueError("Catalogue region IDs do not match source regions")

    catalogue = {
        "description": "OSMFR Europe 3 hillshade HGT tile catalogue",
        "margin_degrees": MARGIN,
        "region_count": len(results),
        "regions": results,
    }
    OUTPUT_FILE.write_text(json.dumps(catalogue, indent=2) + "\n")

    total = sum(len(item["tiles"]) for item in results)
    print(f"Wrote: {OUTPUT_FILE.relative_to(ROOT)}")
    print(f"Regions: {len(results)}")
    print(f"Region tile entries: {total}")
    print(
        "Yorkshire and the Humber:",
        next(
            (item["tiles"] for item in results
             if item["id"] == "yorkshire_and_the_humber"),
            "NOT FOUND",
        ),
    )


if __name__ == "__main__":
    main()
