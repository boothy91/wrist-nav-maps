# wrist-nav-maps

Auto-generated lightweight Mapsforge `.map` files for [WristNav](https://github.com/boothy91/wrist-nav-maps), built monthly from OpenStreetMap data via Geofabrik.

Maps are filtered to hiking/navigation relevant data only (highways, paths, waterways, natural features) keeping file sizes small for Wear OS storage.

## Downloads

Each region group has a permanent release URL. Maps are rebuilt monthly.

| Region | Index | Release Tag |
|--------|-------|-------------|
| Africa | [index.json](https://github.com/boothy91/wrist-nav-maps/releases/download/maps-africa/index.json) | `maps-africa` |
| Asia | [index.json](https://github.com/boothy91/wrist-nav-maps/releases/download/maps-asia/index.json) | `maps-asia` |
| Europe (A-L) | [index.json](https://github.com/boothy91/wrist-nav-maps/releases/download/maps-europe-1/index.json) | `maps-europe-1` |
| Europe (M-Z) | [index.json](https://github.com/boothy91/wrist-nav-maps/releases/download/maps-europe-2/index.json) | `maps-europe-2` |
| Europe - UK | [index.json](https://github.com/boothy91/wrist-nav-maps/releases/download/maps-europe-uk/index.json) | `maps-europe-uk` |
| North America | [index.json](https://github.com/boothy91/wrist-nav-maps/releases/download/maps-north-america/index.json) | `maps-north-america` |
| Others | [index.json](https://github.com/boothy91/wrist-nav-maps/releases/download/maps-others/index.json) | `maps-others` |

## Example URLs

```
# South Yorkshire
https://github.com/boothy91/wrist-nav-maps/releases/download/maps-europe-uk/south-yorkshire.map

# Bayern
https://github.com/boothy91/wrist-nav-maps/releases/download/maps-europe-1/bayern.map

# Index for UK maps
https://github.com/boothy91/wrist-nav-maps/releases/download/maps-europe-uk/index.json
```

## Map Coverage

- **512 regions** across 9 continents
- Includes countries, states, and sub-regions where available
- Smallest available granularity used where possible (e.g. UK counties, German Bezirke)

## Build Schedule

| Workflow | Schedule |
|----------|----------|
| Africa | 1st of month |
| Asia | 2nd of month |
| Europe (A-L) | 3rd of month |
| Europe (M-Z) | 4th of month |
| Europe - UK | 5th of month |
| North America | 6th of month |
| Others | 7th of month |

## Data Sources

- OSM data: [Geofabrik](https://download.geofabrik.de)
- Map format: [Mapsforge](https://github.com/mapsforge/mapsforge)
- Map writer: mapsforge-map-writer 0.21.0
