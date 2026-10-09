kill = "{delete name; delete brand; delete operator; delete ref; delete cuisine}"
keys = ["shop","amenity","tourism","leisure","office","craft","healthcare","historic"]
open("garmin-style/points","w").write("".join(k+"=* "+kill+"\n" for k in keys))
pk = ["building","landuse","amenity","shop","tourism","leisure","office"]
open("garmin-style/polygons","w").write("".join(k+"=* "+kill+"\n" for k in pk))
print("rewrote garmin-style/points and polygons")
