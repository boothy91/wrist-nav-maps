p = "garmin-style/points"
rules = (
 "shop=* {deletealltags}\n"
 "office=* {deletealltags}\n"
 "craft=* {deletealltags}\n"
 "amenity ~ '(bank|atm|fast_food|restaurant|fuel|car_wash|car_rental|hairdresser|pharmacy|dentist|doctors|clinic|veterinary|post_office|post_box|telephone|recycling|vending_machine|charging_station)' {deletealltags}\n"
)
t = open(p).read()
if "shop=* {deletealltags}" not in t:
    open(p, "w").write(rules + t)
print(open(p).read())
