import datetime

from astral import sun, moon, LocationInfo

# Essen, Germany
#   https://www.laengengrad-breitengrad.de/gps-koordinaten-von-essen
location = LocationInfo(
    name="Essen",
    region="NRW",
    timezone="Europe/Berlin",
    latitude=51.4556432,
    longitude=7.0115552,
)

date = datetime.datetime(2023, 4, 20, tzinfo=location.tzinfo)

# Bei der Sonne ist im April der Unterschied ueber den ganzen Monat
# nicht so gross. Von Anfang bis Ende verschiebt sich Sonnenaufgang
# um 50 Minuten und der Sonnenuntergang auch um etwa 50 Minuten.
s = sun.sun(location.observer, date=date)

# Mond wechselt sehr schnell, jeden mehr als eine Stunde
# Unterschied in der Uhrzeit von Mondaufgang und Monduntergang.
# Und an manchen Tagen ist der Mond richtig lange da, 14 Stunden
# oder mehr.
# An manchen Tagen geht der Mond nur tagsueber auf und nachts
# garnicht.
m_rise = moon.moonrise(location.observer, date=date)
m_set = moon.moonset(location.observer, date=date)

# ----------------
# ----------------

print(dir(moon))

print('\n\n\n')

print(s)

print("---")

print(m_rise)
print(m_set)
