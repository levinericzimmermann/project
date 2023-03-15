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

    try:
        mr = moon.moonrise(observer=location.observer, date=date)
    except ValueError:
        pass
    else:
        print("\tmoonrise", mr.time())
    try:
        ms = moon.moonset(observer=location.observer, date=date)
    except ValueError:
        pass
    else:
        print("\tmoonset\t", ms.time())


    print("---\n\n")
