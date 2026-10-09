p = "garmin-style/lines"
rule = "highway=* {delete name}\n"
t = open(p).read()
if rule not in t:
    open(p, "w").write(rule + t)
print(open(p).read()[:400])
