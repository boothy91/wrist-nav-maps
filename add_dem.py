import glob, re

STEP = """      - name: Download elevation (SRTM HGT, auto tiles)
        run: |
          mkdir -p hgt
          python3 - <<'PY' > hgt_tiles.txt
          import math
          lons, lats = [], []
          for l in open('split/areas.poly'):
              p = l.split()
              if len(p) == 2:
                  try:
                      lons.append(float(p[0])); lats.append(float(p[1]))
                  except ValueError:
                      pass
          for la in range(math.floor(min(lats)), math.floor(max(lats)) + 1):
              for lo in range(math.floor(min(lons)), math.floor(max(lons)) + 1):
                  ns = 'N' if la >= 0 else 'S'
                  ew = 'E' if lo >= 0 else 'W'
                  print('%s%02d%s%03d' % (ns, abs(la), ew, abs(lo)))
          PY
          cat hgt_tiles.txt
          for t in $(cat hgt_tiles.txt); do
            d=${t:0:3}
            curl -sf --retry 5 "https://s3.amazonaws.com/elevation-tiles-prod/skadi/${d}/${t}.hgt.gz" -o "hgt/${t}.hgt.gz" && gunzip -f "hgt/${t}.hgt.gz" || echo "missing ${t}"
          done
          ls -lh hgt

"""
OPTS = ["--dem=hgt \\", "--dem-poly=split/areas.poly \\",
        "--dem-dists=3312,13248,26512,53024 \\", "--overview-dem-dist=88888 \\"]

for wf in glob.glob(".github/workflows/*.y*ml"):
    t = open(wf).read()
    if "mkgmap" not in t:
        continue
    lines = t.split("\n")
    # drop any earlier DEM download step
    out, skip = [], False
    for ln in lines:
        if "- name: Download elevation" in ln:
            skip = True
            continue
        if skip and ln.startswith("      - name:"):
            skip = False
        if not skip:
            out.append(ln)
    lines, out = out, []
    step_done = opt_done = False
    has_dem = any("--dem=" in l for l in lines)
    for ln in lines:
        if not step_done and "- name: Build Garmin IMG" in ln:
            out.append(STEP.rstrip("\n") + "\n")
            step_done = True
        out.append(ln)
        if not has_dem and not opt_done and ln.strip() == "--gmapsupp \\":
            ind = ln[:len(ln) - len(ln.lstrip())]
            out += [ind + o for o in OPTS]
            opt_done = True
    if step_done:
        open(wf, "w").write("\n".join(out))
        print("patched", wf)
    else:
        print("no 'Build Garmin IMG' step in", wf)
