import datetime

# First import project to activate constant + patches
import project

from astral import LocationInfo, sun, Depression

from mutwo import core_converters
from mutwo import diary_interfaces
from mutwo import project_converters


def make_part(location_info, d, day_light):
    if allowed_date_list and not any(
        [
            d.day == d2.day and d.month == d2.month and d.year == d2.year
            for d2 in allowed_date_list
        ]
    ):
        return
    if allowed_day_light_list and day_light not in allowed_day_light_list:
        return
    astral_event = project_converters.DatetimeToSimultaneousEvent(
        location_info
    ).convert(d)
    clock_tuple = project_converters.AstralEventToClockTuple(
        project_converters.AstralConstellationToOrchestration(
            project.constants.MOON_PHASE_TO_INTONATION,
            project.constants.SUN_LIGHT_TO_PITCH_INDEX_TUPLE,
            project.constants.MOON_LIGHT_TO_PITCH_INDEX_TUPLE,
        ),
        project_converters.AstralConstellationToScale(
            project.constants.MOON_PHASE_TO_INTONATION,
            project.constants.SUN_LIGHT_TO_PITCH_INDEX_TUPLE,
            project.constants.MOON_LIGHT_TO_PITCH_INDEX_TUPLE,
        ),
    ).convert(astral_event)

    project.render.midi(clock_tuple)
    if day_light == "dawn":
        project.render.notation(clock_tuple)


allowed_date_list = [datetime.datetime(2023, 4, 30)]
allowed_day_light_list = ["dawn"]

if __name__ == "__main__":
    location_info = LocationInfo(
        name="Essen",
        region="NRW",
        timezone="Europe/Berlin",
        latitude=51.4556432,
        longitude=7.0115552,
    )

    with diary_interfaces.open():
        april = tuple(datetime.datetime(2023, 4, d) for d in range(1, 31))
        for day in april:
            print(f"RENDER '{day}'!")
            s = sun.sun(
                location_info.observer, date=day, dawn_dusk_depression=Depression.CIVIL
            )
            for day_light in ("dawn", "sunrise", "sunset", "dusk"):
                d = s[day_light]
                make_part(location_info, d, day_light)
