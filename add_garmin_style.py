import os, glob
S = "garmin-style"
os.makedirs(S, exist_ok=True)
F = {
"info": "description: WristNav declutter\nbase-style: default\n",
"version": "1\n",
"points": "shop=* {delete name}\namenity=* {delete name}\ntourism=* {delete name}\nleisure=* {delete name}\noffice=* {delete name}\ncraft=* {delete name}\n",
"lines": "highway ~ '(residential|service|unclassified|living_street|track|path|footway|cycleway|bridleway|steps|pedestrian|road)' {delete name}\nwaterway=* {delete name}\n",
"polygons": "building=* {delete name}\nlanduse=* {delete name}\namenity=* {delete name}\nshop=* {delete name}\n",
}
for n, c in F.items():
    open(os.path.join(S, n), "w").write(c)
print("wrote", S)
for wf in glob.glob(".github/workflows/*.y*ml"):
    t = open(wf).read()
    if "mkgmap" not in t or "--style-file" in t:
        continue
    out, done = [], False
    for line in t.split("\n"):
        out.append(line)
        if not done and line.strip() == "--gmapsupp \\":
            out.append(line[:len(line) - len(line.lstrip())] + "--style-file=garmin-style \\")
            done = True
    if done:
        open(wf, "w").write("\n".join(out))
        print("patched", wf)
