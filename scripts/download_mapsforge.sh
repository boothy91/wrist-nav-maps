#!/bin/bash
set -e

REPO="boothy91/wrist-nav-maps"
WORKDIR=~/map_builds
mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "=== Downloading Far Eastern Federal District ==="
echo "--- Part 1 (1.5G) ---"
wget --progress=bar:force --timeout=600 --tries=2 \
  -O far-eastern-fed-district-1.map \
  "https://download.mapsforge.org/maps/v5/russia/far-eastern-fed-district-1.map"

echo "--- Part 2 (52M) ---"
wget --progress=bar:force --timeout=600 --tries=2 \
  -O far-eastern-fed-district-2.map \
  "https://download.mapsforge.org/maps/v5/russia/far-eastern-fed-district-2.map"

echo "--- Uploading to maps-others ---"
gh release upload maps-others far-eastern-fed-district-1.map --clobber --repo $REPO
gh release upload maps-others far-eastern-fed-district-2.map --clobber --repo $REPO
rm -f far-eastern-fed-district-1.map far-eastern-fed-district-2.map
echo "Done: Far Eastern uploaded"

echo ""
echo "=== Downloading New Zealand ==="
echo "--- Part 1 (373M) ---"
wget --progress=bar:force --timeout=600 --tries=2 \
  -O new-zealand-1.map \
  "https://download.mapsforge.org/maps/v5/australia-oceania/new-zealand-1.map"

echo "--- Part 2 (356M) ---"
wget --progress=bar:force --timeout=600 --tries=2 \
  -O new-zealand-2.map \
  "https://download.mapsforge.org/maps/v5/australia-oceania/new-zealand-2.map"

echo "--- Uploading to maps-others ---"
gh release upload maps-others new-zealand-1.map --clobber --repo $REPO
gh release upload maps-others new-zealand-2.map --clobber --repo $REPO
rm -f new-zealand-1.map new-zealand-2.map
echo "Done: New Zealand uploaded"

echo ""
echo "=== All done ==="
