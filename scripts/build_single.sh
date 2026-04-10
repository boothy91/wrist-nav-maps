#!/bin/bash
REGION_ID=$1
REGION_NAME=$2
PBF_URL=$3
RELEASE_TAG=$4

OSMOSIS_HOME=~/alaska_test/osmosis_install/osmosis-0.49.2
export JAVACMD_OPTIONS=-Xmx7500m

mkdir -p ~/map_builds
cd ~/map_builds

FNAME="${REGION_ID/\//-}.map"

echo "=== Building $REGION_NAME ==="
wget --timeout=300 --tries=2 -O region.osm.pbf "$PBF_URL"

osmium tags-filter region.osm.pbf \
  w/highway w/path w/footway w/bridleway \
  w/track w/waterway w/natural w/landuse \
  -o region_filtered.osm.pbf --overwrite

$OSMOSIS_HOME/bin/osmosis --rb file=region_filtered.osm.pbf --mw file="$FNAME" type=hd

ls -lh "$FNAME"
gh release upload "$RELEASE_TAG" "$FNAME" --clobber --repo boothy91/wrist-nav-maps
echo "=== Done: $FNAME uploaded to $RELEASE_TAG ==="
