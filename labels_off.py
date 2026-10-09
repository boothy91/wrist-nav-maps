kill = ("delete name; delete brand; delete operator; delete ref; delete int_ref; "
        "delete nat_ref; delete reg_ref; delete cuisine; delete mkgmap:boundary_name")
addr = "addr:housenumber=* {delete addr:housenumber; delete addr:housename}\n"
open("garmin-style/points", "w").write(
 "# Keep only places, natural features, water, viewpoints, barriers\n"
 "place!=* & natural!=* & waterway!=* & landuse!=reservoir & landuse!=basin"
 " & barrier!=* & tourism!=viewpoint {deletealltags}\n")
open("garmin-style/lines", "w").write(
 addr + "waterway!=* & natural!=* {" + kill + "}\n")
open("garmin-style/polygons", "w").write(
 addr + "natural!=* & waterway!=* & place!=* & landuse!=reservoir & landuse!=basin {"
 + kill + "}\n")
print("rewrote points, lines, polygons")
