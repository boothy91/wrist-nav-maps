#!/bin/bash

REPO="boothy91/wrist-nav-maps"

echo "Fetching release assets..."

# Get all uploaded .map files from all releases
UPLOADED=$(gh release list --repo $REPO --limit 50 --json tagName --jq '.[].tagName' | while read tag; do
    gh release view "$tag" --repo $REPO --json assets --jq '.assets[].name'
done | grep '\.map$' | sort)

echo "Fetching regions from config..."

# Get all expected map filenames from region JSONs
EXPECTED=$(python3 -c "
import json, glob
for f in sorted(glob.glob('config/regions/regions-*.json')):
    with open(f) as fh:
        regions = json.load(fh)
    for r in regions:
        rid = r['id'].replace('/', '-')
        print(rid + '.map')
" | sort)

echo ""
echo "=== MISSING FROM RELEASES ==="
comm -23 <(echo "$EXPECTED") <(echo "$UPLOADED")

echo ""
echo "=== TOTALS ==="
echo "Expected: $(echo "$EXPECTED" | wc -l)"
echo "Uploaded: $(echo "$UPLOADED" | wc -l)"
echo "Missing:  $(comm -23 <(echo "$EXPECTED") <(echo "$UPLOADED") | wc -l)"
