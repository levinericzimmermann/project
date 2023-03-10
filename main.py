import datetime

from astral import LocationInfo

from mutwo import core_converters
from mutwo import diary_interfaces
from mutwo import project_converters

import project


if __name__ == "__main__":
    # ==============================
    # Fast imitation of what happens inside of walkman:
    #
    #   - check current time
    #   - create from this time clock_tuple (based on entries and converter)
    #   - render this clock_tuple to real-world sounds
    #
    # ==============================

    location_info = LocationInfo(
        name="Essen",
        region="NRW",
        timezone="Europe/Berlin",
        latitude=51.4556432,
        longitude=7.0115552,
    )

    d = datetime.datetime.now(location_info.tzinfo)
    astral_event = project_converters.DatetimeToSimultaneousEvent(
        location_info
    ).convert(d)
    with diary_interfaces.open():
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

    print(clock_tuple)

    project.render.midi(clock_tuple)
    project.render.notation(clock_tuple)
