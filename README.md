# WristNav Maps

Auto-generated `.map` files for [WristNav](https://github.com/Boothy91/Wrist-Nav-Source) — a standalone Wear OS hiking and trail running navigation app.

## How it works

A GitHub Action runs on the 1st of every month:
1. Downloads PBF data from [Geofabrik](https://download.geofabrik.de)
2. Filters to hiking-relevant tags (highways, paths, waterways, contours etc.)
3. Converts to Mapsforge `.map` format using Osmosis
4. Publishes all maps as assets on the `maps-latest` release

## Download

Maps are available on the [latest release](../../releases/tag/maps-latest).

Direct URL pattern:
```
https://github.com/Boothy91/wrist-nav-maps/releases/download/maps-latest/{region-id}.map
```

## Index

The `index.json` file lists all available maps with URLs and file sizes:
```
https://github.com/Boothy91/wrist-nav-maps/releases/download/maps-latest/index.json
```

## Adding regions

Edit `config/regions.json` to add new regions. Each entry needs:
```json
{
  "id": "south-yorkshire",
  "name": "South Yorkshire",
  "path": "europe/united-kingdom/england",
  "pbf": "https://download.geofabrik.de/europe/united-kingdom/england/south-yorkshire-latest.osm.pbf"
}
```

Then trigger the workflow manually via Actions → Build and Release Maps → Run workflow.
