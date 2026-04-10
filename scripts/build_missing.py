import json, subprocess, os

tmpdir = os.environ.get('TMPDIR', '/tmp')

with open(f'{tmpdir}/missing_regions.json') as f:
    missing = json.load(f)

osmosis = os.path.expanduser('~/wrist-nav-maps/osmosis_install/osmosis-0.49.2/bin/osmosis')

for r in missing:
    print(f"\n=== Building {r['name']} ===")
    pbf = f'{tmpdir}/region.osm.pbf'
    filtered = f'{tmpdir}/region_filtered.osm.pbf'
    outfile = os.path.expanduser(f"~/map_builds/{r['fname']}")

    ret = subprocess.run(['wget', '--timeout=300', '--tries=2', '-O', pbf, r['pbf']])
    if ret.returncode != 0:
        print(f"FAILED to download {r['name']}")
        continue

    ret = subprocess.run(['osmium', 'tags-filter', pbf,
        'w/highway', 'w/path', 'w/footway', 'w/bridleway',
        'w/track', 'w/waterway', 'w/natural', 'w/landuse',
        '-o', filtered, '--overwrite'])
    if ret.returncode != 0:
        print(f"FAILED to filter {r['name']}")
        continue

    ret = subprocess.run([osmosis, '--rb', f'file={filtered}', '--mw', f'file={outfile}', 'type=hd'])
    if ret.returncode != 0:
        print(f"FAILED to convert {r['name']}")
        continue

    ret = subprocess.run(['gh', 'release', 'upload', r['release'], outfile, '--clobber', '--repo', 'boothy91/wrist-nav-maps'])
    if ret.returncode != 0:
        print(f"FAILED to upload {r['name']}")
        continue

    os.remove(pbf)
    os.remove(filtered)
    os.remove(outfile)
    print(f"Done: {r['fname']} uploaded to {r['release']}")

print("\nAll done!")
