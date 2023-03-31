import datetime
import os

from astral import LocationInfo
from mutwo import project_generators

import project

lunar_phase = project_generators.LunarPhaseCalculator()

location_info = LocationInfo(
    name="Essen",
    region="NRW",
    timezone="Europe/Berlin",
    latitude=51.4556432,
    longitude=7.0115552,
)
location_info.elevation = 100

april = tuple(
    datetime.datetime(2023, 4, d, tzinfo=location_info.tzinfo) for d in range(1, 31)
)
day_light_list = [f"etc/suncycle/sun_1_landscape.pdf", "etc/blank.pdf"]
for i, day in enumerate(april):
    path = f"etc/daylight/{i}/{i}.pdf"
    if not os.path.exists(path):
        break
    p = lunar_phase(day, location_info)
    day_light_list.append(f"etc/mooncycle/m{p}_landscape.pdf")
    day_light_list.append(path)

project.render.merge_notation("sunrise", day_light_list)
