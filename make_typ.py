#!/usr/bin/env python3
"""Run from the root of the wrist-nav-maps repo:  python3 make_typ.py
Writes typ.txt (colour theme for mkgmap's default style types) and adds it
to the Garmin workflow's mkgmap command. Safe to run twice."""
import glob, re

# ---- polygons: type -> (colour, draw level). Level: higher draws on top.
P = {
 0x32:("#AAD3DF",1),                                   # sea
 0x4e:("#F2EFC9",2), 0x10:("#EAE5DA",2), 0x17:("#CDEBB0",2),
 0x0c:("#E3D3E3",2), 0x4f:("#C8DFA8",2), 0x1f:("#F0E4F0",2),
 0x03:("#EAE5DA",2), 0x05:("#EEEEEE",2), 0x06:("#E2E2E2",2),
 0x07:("#E8DEE8",2), 0x08:("#F2DCCF",2), 0x0a:("#F4F0C0",2),
 0x0b:("#F6D6D6",2), 0x04:("#E4D2D2",2), 0x1e:("#E8D8C8",2),
 0x16:("#D6EBD2",3), 0x18:("#B8E0A0",3), 0x19:("#BCE6B0",3),
 0x1a:("#AACBAF",3), 0x50:("#A3CC8E",3), 0x51:("#B6DDD0",3),
 0x4d:("#E8F4FF",3), 0x09:("#BFDFF5",3),
 0x3c:("#9CC3F0",4), 0x3d:("#AAD3DF",4), 0x3f:("#9CC3F0",4),
 0x46:("#9CC3F0",4), 0x47:("#9CC3F0",4), 0x53:("#EAE5DA",4),
 0x13:("#D2C2AE",5), 0x0e:("#C8C8C8",5),
}

# ---- lines: type -> (width, border, fill, border colour)
L = {
 0x01:(4,1,"#E892A2","#C0285A"), 0x09:(3,1,"#E892A2","#C0285A"),
 0x02:(4,1,"#F9B29C","#B84A32"), 0x03:(4,1,"#FCD6A4","#C98A30"),
 0x08:(3,1,"#FCD6A4","#C98A30"), 0x04:(3,1,"#F7F4A8","#B8B050"),
 0x05:(3,1,"#FFFFFF","#8A8A8A"), 0x06:(2,1,"#FFFFFF","#A0A0A0"),
 0x07:(1,0,"#B0B0B0",None),
 0x10801:(4,1,"#F9B29C","#B84A32"), 0x10802:(4,1,"#FCD6A4","#C98A30"),
 0x10803:(3,1,"#F7F4A8","#B8B050"), 0x10804:(3,1,"#FFFFFF","#8A8A8A"),
 0x18:(1,0,"#8FB8F0",None), 0x1f:(3,0,"#8FB8F0",None),
 0x26:(1,0,"#8FB8F0",None),  0x10A02:(1,0,"#8FB8F0",None),
 0x14:(2,1,"#777777","#FFFFFF"), 0x15:(1,0,"#4A90C0",None),
 0x29:(1,0,"#AAAAAA",None),
}
# dashed (pixmap) lines: type -> (colour, rows)
D = {
 0x16:("#B84B3A",2),   # footpath / path / steps
 0x0a:("#8B5A2B",3),   # track
 0x1b:("#5090D0",2),   # ferry
 0x1c:("#A060A0",1), 0x1d:("#A060A0",1), 0x1e:("#8040A0",2),  # boundaries
}

# every polygon type the default style can emit (else it would be hidden)
ALL_POLY = set(P)
try:
    txt = open("polygon_types.txt").read()
    ALL_POLY |= {int(x, 16) for x in txt.split()}
except OSError:
    pass
ALL_POLY |= {0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0e,
 0x10,0x13,0x16,0x17,0x18,0x19,0x1a,0x1e,0x1f,0x32,0x3c,0x3d,0x3f,0x46,0x47,
 0x4d,0x4e,0x4f,0x50,0x51,0x53}

def h(t): return "0x%x" % t
o = ["; WristNav Garmin theme for the mkgmap default style",
     "[_id]","FID=6800","ProductCode=1","CodePage=1252","[end]","","[_drawOrder]"]
for t in sorted(ALL_POLY):
    o.append("Type=%s,%d" % (h(t), P.get(t,("",3))[1]))
o += ["[end]",""]
for t,(c,_) in sorted(P.items()):
    o += ["[_polygon]","Type="+h(t),"FontStyle=NoLabel",'Xpm="0 0 1 0"','"a c %s"'%c,"[end]",""]
for t,(w,b,f,bc) in sorted(L.items()):
    o += ["[_line]","Type="+h(t),"LineWidth=%d"%w]
    if b and bc:
        o += ["BorderWidth=%d"%b,'Xpm="0 0 2 0"','"a c %s"'%f,'"b c %s"'%bc]
    else:
        o += ['Xpm="0 0 1 0"','"a c %s"'%f]
    o += ["[end]",""]
for t,(c,rows) in sorted(D.items()):
    row = "a"*12 + "b"*8 + "a"*4 + "b"*8
    assert len(row)==32
    o += ["[_line]","Type="+h(t),'Xpm="32 %d 2 1"'%rows,'"a c %s"'%c,'"b c none"']
    o += ['"%s"'%row]*rows
    o += ["[end]",""]
open("typ.txt","w").write("\n".join(o)+"\n")
print("wrote typ.txt:", len(P), "polygons,", len(L)+len(D), "lines")

for wf in glob.glob(".github/workflows/*.y*ml"):
    t = open(wf).read()
    if "mkgmap" not in t or "typ.txt" in t: continue
    out, done = [], False
    for line in t.split("\n"):
        if not done and line.strip() == "-c split/template.args":
            ind = line[:len(line)-len(line.lstrip())]
            out += [line + " \\", ind + "typ.txt"]
            done = True
        else:
            out.append(line)
    if done:
        open(wf,"w").write("\n".join(out)); print("patched", wf)
