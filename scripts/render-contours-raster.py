#!/usr/bin/env python3
"""Render contour GeoJSON-sequence features as transparent XYZ PNG tiles."""

import argparse
import json
import math
import os
import sys
import zipfile
from collections import OrderedDict
from pathlib import Path

from PIL import Image, ImageDraw

TILE_SIZE = 256
MAX_LAT = 85.0511287798066
CACHE_LIMIT = 128

STYLES = {
    "elevation_major": (116, 83, 55, 220, 2),
    "elevation_medium": (145, 119, 91, 185, 1),
    "elevation_minor": (158, 145, 125, 145, 1),
}
MIN_ZOOM = {
    "elevation_major": 8,
    "elevation_medium": 10,
    "elevation_minor": 12,
}


def world_pixel(lon, lat, zoom):
    lat = max(-MAX_LAT, min(MAX_LAT, lat))
    scale = TILE_SIZE * (2 ** zoom)
    x = (lon + 180.0) / 360.0 * scale
    sin_lat = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + sin_lat) / (1 - sin_lat)) / (4 * math.pi)) * scale
    return x, y


class TileRenderer:
    def __init__(self, root, min_zoom, max_zoom):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.cache = OrderedDict()
        self.tile_paths = set()
        self.feature_count = 0
        self.line_count = 0
        self.class_counts = {key: 0 for key in STYLES}

    def tile_path(self, z, x, y):
        return self.root / str(z) / str(x) / f"{y}.png"

    def get_tile(self, z, x, y):
        key = (z, x, y)
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]

        if len(self.cache) >= CACHE_LIMIT:
            old_key, old_image = self.cache.popitem(last=False)
            self.save_tile(old_key, old_image)

        path = self.tile_path(z, x, y)
        if path.is_file():
            image = Image.open(path).convert("RGBA")
        else:
            image = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))

        self.cache[key] = image
        return image

    def save_tile(self, key, image):
        path = self.tile_path(*key)
        if image.getbbox():
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(path, format="PNG", optimize=False)
            self.tile_paths.add(path)
        else:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        image.close()

    def draw_line(self, coords, contour_class):
        if len(coords) < 2:
            return

        colour_r, colour_g, colour_b, alpha, width = STYLES[contour_class]
        colour = (colour_r, colour_g, colour_b, alpha)
        first_zoom = MIN_ZOOM[contour_class]

        for zoom in range(max(first_zoom, self.min_zoom), self.max_zoom + 1):
            points = []
            for coord in coords:
                if len(coord) < 2:
                    continue
                try:
                    lon, lat = float(coord[0]), float(coord[1])
                except (ValueError, TypeError):
                    continue
                if not math.isfinite(lon) or not math.isfinite(lat):
                    continue
                points.append(world_pixel(lon, lat, zoom))

            if len(points) < 2:
                continue

            world_tiles = 2 ** zoom
            for (x1, y1), (x2, y2) in zip(points, points[1:]):
                min_tx = max(0, int(math.floor(min(x1, x2) / TILE_SIZE)))
                max_tx = min(world_tiles - 1, int(math.floor(max(x1, x2) / TILE_SIZE)))
                min_ty = max(0, int(math.floor(min(y1, y2) / TILE_SIZE)))
                max_ty = min(world_tiles - 1, int(math.floor(max(y1, y2) / TILE_SIZE)))

                for tx in range(min_tx, max_tx + 1):
                    for ty in range(min_ty, max_ty + 1):
                        image = self.get_tile(zoom, tx, ty)
                        draw = ImageDraw.Draw(image, "RGBA")
                        offset_x = tx * TILE_SIZE
                        offset_y = ty * TILE_SIZE
                        draw.line(
                            (x1 - offset_x, y1 - offset_y,
                             x2 - offset_x, y2 - offset_y),
                            fill=colour,
                            width=width,
                        )
                        del draw

        self.line_count += 1

    def add_feature(self, feature):
        if feature.get("type") != "Feature":
            return

        props = feature.get("properties") or {}
        tags = props.get("tags") if isinstance(props.get("tags"), dict) else props
        contour_class = tags.get("contour_ext") or tags.get("contour")
        if contour_class not in STYLES:
            return

        geometry = feature.get("geometry") or {}
        kind = geometry.get("type")
        coordinates = geometry.get("coordinates")
        if not coordinates:
            return

        self.feature_count += 1
        self.class_counts[contour_class] += 1

        if kind == "LineString":
            self.draw_line(coordinates, contour_class)
        elif kind == "MultiLineString":
            for line in coordinates:
                self.draw_line(line, contour_class)

    def compress_tiles(self):
        """Drop fully transparent tiles, palette-quantize the rest."""
        for path in list(self.root.rglob("*.png")):
            with Image.open(path) as src:
                rgba = src.convert("RGBA")
            if rgba.getchannel("A").getbbox() is None:
                path.unlink()
                continue
            small = rgba.quantize(colors=8, method=Image.FASTOCTREE)
            small.save(path, optimize=True)

    def finish(self):
        for key, image in list(self.cache.items()):
            self.save_tile(key, image)
        self.cache.clear()

        # Some tiles may have been reopened and rewritten; count actual PNGs.
        self.compress_tiles()
        tiles = sorted(self.root.rglob("*.png"))
        if not tiles:
            raise RuntimeError(
                "No contour tiles were rendered. Check GeoJSON tags and input data."
            )

        return tiles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Output ZIP path")
    parser.add_argument("--min-zoom", type=int, default=8)
    parser.add_argument("--max-zoom", type=int, default=16)
    args = parser.parse_args()

    if args.min_zoom < 0 or args.max_zoom > 20 or args.min_zoom > args.max_zoom:
        parser.error("Zoom range must satisfy 0 <= min-zoom <= max-zoom <= 20")

    # Classes retain their own minimum zoom; do not silently render below them.
    work_root = Path(args.output).with_suffix(".tiles")
    if work_root.exists():
        import shutil
        shutil.rmtree(work_root)

    renderer = TileRenderer(work_root, args.min_zoom, args.max_zoom)
    try:
        for line_number, raw in enumerate(sys.stdin, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                renderer.add_feature(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid GeoJSON-sequence record on line {line_number}: {exc}"
                ) from exc

        tiles = renderer.finish()
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(
            output, "w", compression=zipfile.ZIP_STORED, allowZip64=True
        ) as archive:
            for path in tiles:
                archive.write(path, path.relative_to(work_root).as_posix())

        print(f"Features rendered: {renderer.feature_count}")
        print(f"Line strings rendered: {renderer.line_count}")
        print(f"PNG tiles: {len(tiles)}")
        print(f"ZIP bytes: {output.stat().st_size}")
        print(f"Class counts: {json.dumps(renderer.class_counts, sort_keys=True)}")
    finally:
        import shutil
        shutil.rmtree(work_root, ignore_errors=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
