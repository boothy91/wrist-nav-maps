import json, glob, os

tmpdir = os.environ.get('TMPDIR', '/tmp')

with open(f'{tmpdir}/uploaded_maps.txt') as f:
    uploaded = set(line.strip() for line in f if line.strip())

tag_map = {
    'regions-africa.json': 'maps-africa',
    'regions-asia.json': 'maps-asia',
    'regions-australia-oceania.json': 'maps-others',
    'regions-central-america.json': 'maps-others',
    'regions-europe.json': 'maps-europe',
    'regions-europe-1.json': 'maps-europe',
    'regions-europe-2.json': 'maps-europe',
    'regions-europe-uk.json': 'maps-europe-uk',
    'regions-north-america.json': 'maps-north-america',
    'regions-south-america.json': 'maps-others',
    'regions-others.json': 'maps-others',
}

missing = []
for f in sorted(glob.glob(os.path.expanduser('~/wrist-nav-maps/config/regions/regions-*.json'))):
    basename = f.split('/')[-1]
    release = tag_map.get(basename, 'maps-others')
    with open(f) as fh:
        regions = json.load(fh)
    for r in regions:
        fname = r['id'].replace('/', '-') + '.map'
        if fname not in uploaded:
            missing.append({'id': r['id'], 'name': r['name'], 'pbf': r['pbf'], 'release': release, 'fname': fname})

with open(f'{tmpdir}/missing_regions.json', 'w') as f:
    json.dump(missing, f, indent=2)

print(f"Found {len(missing)} missing maps:")
for m in missing:
    print(f"  {m['name']} -> {m['release']}")
