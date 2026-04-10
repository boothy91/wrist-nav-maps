#!/bin/bash
# Builds the 4 missing maps on Termux and uploads to GitHub releases
# Run from anywhere: bash ~/wrist-nav-maps/scripts/build_missing_termux.sh

set -e

REPO="boothy91/wrist-nav-maps"
OSMOSIS_HOME=~/wrist-nav-maps/osmosis_install/osmosis-0.49.2
export JAVACMD_OPTIONS=-Xmx7500m

WORKDIR=~/map_builds
mkdir -p "$WORKDIR"
cd "$WORKDIR"

# Check osmosis exists
if [ ! -f "$OSMOSIS_HOME/bin/osmosis" ]; then
  echo "ERROR: osmosis not found at $OSMOSIS_HOME"
  echo "Check the path is correct"
  exit 1
fi

echo "=== Finding missing maps ==="

# Get all uploaded map filenames from all releases
UPLOADED=$(gh release list --repo $REPO --limit 50 --json tagName --jq '.[].tagName' | while read tag; do
  gh release view "$tag" --repo $REPO --json assets --jq '.assets[].name' 2>/dev/null
done | grep '\.map$' | sort)

# Find missing regions from config
python3 << PYEOF > $TMPDIR/missing_maps.sh
import json, glob, subprocess

uploaded = set("""$UPLOADED""".strip().split('\n'))

tag_map = {
    'regions-africa':        'maps-africa',
    'regions-asia':          'maps-asia',
    'regions-europe-1':      'maps-europe',
    'regions-europe-2':      'maps-europe',
    'regions-europe-uk':     'maps-europe-uk',
    'regions-north-america': 'maps-north-america',
    'regions-others':        'maps-others',
}

missing = []
for f in sorted(glob.glob('$HOME/wrist-nav-maps/config/regions/regions-*.json')):
    key = f.split('/')[-1].replace('.json', '')
    release = tag_map.get(key, 'maps-others')
    with open(f) as fh:
        data = json.load(fh)
    for r in data:
        fname = r['id'].replace('/', '-') + '.map'
        if fname not in uploaded:
            missing.append((r['id'], r['name'], r['pbf'], release, fname))

if not missing:
    print('echo "All maps already uploaded!"')
else:
    for rid, name, pbf, release, fname in missing:
        print(f'build_one "{rid}" "{name}" "{pbf}" "{release}" "{fname}"')
PYEOF

# Count missing
MISSING_COUNT=$(grep -c 'build_one' $TMPDIR/missing_maps.sh 2>/dev/null || echo 0)

if [ "$MISSING_COUNT" -eq 0 ]; then
  echo "All maps already uploaded!"
  exit 0
fi

echo "Found $MISSING_COUNT missing maps"
echo ""

# Build function
build_one() {
  local REGION_ID="$1"
  local REGION_NAME="$2"
  local PBF_URL="$3"
  local RELEASE_TAG="$4"
  local FNAME="$5"

  echo "============================================"
  echo "Building: $REGION_NAME"
  echo "Release:  $RELEASE_TAG"
  echo "File:     $FNAME"
  echo "============================================"

  # Download
  echo "--- Downloading PBF ---"
  wget --progress=bar:force --timeout=600 --tries=2 -O region.osm.pbf "$PBF_URL"
  echo "Downloaded: $(ls -lh region.osm.pbf | awk '{print $5}')"

  # Filter
  echo "--- Filtering with osmium ---"
  osmium tags-filter region.osm.pbf \
    w/highway w/path w/footway w/bridleway \
    w/track w/waterway w/natural w/landuse \
    -o region_filtered.osm.pbf --overwrite
  echo "Filtered: $(ls -lh region_filtered.osm.pbf | awk '{print $5}')"

  # Convert
  echo "--- Converting with osmosis ---"
  $OSMOSIS_HOME/bin/osmosis \
    --rb file=region_filtered.osm.pbf \
    --mw file="$FNAME" type=hd

  echo "Output: $(ls -lh $FNAME | awk '{print $5}')"

  # Upload
  echo "--- Uploading to $RELEASE_TAG ---"
  gh release upload "$RELEASE_TAG" "$FNAME" --clobber --repo $REPO
  echo "Done: $FNAME"

  # Clean up to free space for next build
  rm -f region.osm.pbf region_filtered.osm.pbf "$FNAME"
  echo ""
}

# Run the missing builds
source $TMPDIR/missing_maps.sh

echo "=== All missing maps built and uploaded ==="
