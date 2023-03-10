import datetime

from astral import sun, moon, LocationInfo, Depression

# Essen, Germany
#   https://www.laengengrad-breitengrad.de/gps-koordinaten-von-essen
location = LocationInfo(
    name="Essen",
    region="NRW",
    timezone="Europe/Berlin",
    latitude=51.4556432,
    longitude=7.0115552,
)

for date in range(1, 31):
    date = datetime.datetime(2023, 4, date, tzinfo=location.tzinfo)

    print(f'april {date.day}\n')
    # Depression.CIVIL seems to be the best, indeed
    s = sun.sun(location.observer, date=date, dawn_dusk_depression=Depression.CIVIL)

    print("\tdawn\t", s["dawn"].time())
    print("\tsunrise\t", s["sunrise"].time())

    print('\t__\n')

    print("\tsunset\t", s["sunset"].time())
    print("\tdusk\t", s["dusk"].time())

    print("---\n\n")
