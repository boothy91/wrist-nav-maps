import glob

for wf in glob.glob(".github/workflows/*.y*ml"):
    t = open(wf).read()
    if "mkgmap" not in t:
        continue
    out, skip = [], False
    for ln in t.split("\n"):
        # drop the elevation download step
        if "- name: Download elevation" in ln:
            skip = True
            continue
        if skip and ln.startswith("      - name:"):
            skip = False
        if skip:
            continue
        # drop DEM options
        s = ln.strip()
        if s.startswith("--dem") or s.startswith("--overview-dem-dist"):
            continue
        out.append(ln)
    # add --merge-lines after --gmapsupp
    if not any("--merge-lines" in l for l in out):
        res = []
        for ln in out:
            res.append(ln)
            if ln.strip() == "--gmapsupp \\":
                ind = ln[:len(ln) - len(ln.lstrip())]
                res.append(ind + "--merge-lines \\")
        out = res
    open(wf, "w").write("\n".join(out))
    print("patched", wf)
