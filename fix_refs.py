p = "garmin-style/lines"
rule = "highway=* {delete ref; delete int_ref; delete nat_ref; delete reg_ref}\n"
t = open(p).read()
if rule not in t:
    open(p, "w").write(rule + t)
print(open(p).read())
