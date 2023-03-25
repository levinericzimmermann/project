from concurrent.futures import ThreadPoolExecutor
import datetime
import time

# First import project to activate constant + patches
import project

from astral import LocationInfo, sun, Depression

from mutwo import clock_converters
from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import project_converters

astral_constellation_to_orchestration = (
    project_converters.AstralConstellationToOrchestration(
        project.constants.MOON_PHASE_TO_INTONATION,
        project.constants.SUN_LIGHT_TO_PITCH_INDEX_TUPLE,
        project.constants.MOON_LIGHT_TO_PITCH_INDEX_TUPLE,
    )
)
astral_constellation_to_scale = project_converters.AstralConstellationToScale(
    project.constants.MOON_PHASE_TO_INTONATION,
    project.constants.SUN_LIGHT_TO_PITCH_INDEX_TUPLE,
    project.constants.MOON_LIGHT_TO_PITCH_INDEX_TUPLE,
)
astral_event_to_clock_tuple = project_converters.AstralEventToClockTuple(
    astral_constellation_to_orchestration,
    astral_constellation_to_scale,
).convert


def run_if_allowed(func):
    def wrapper(d, day_light, *args, **kwargs):
        if allowed_date_list and not any(
            [
                d.day == d2.day and d.month == d2.month and d.year == d2.year
                for d2 in allowed_date_list
            ]
        ):
            return
        if allowed_day_light_list and day_light not in allowed_day_light_list:
            return
        return func(d, day_light, *args, **kwargs)

    return wrapper


@run_if_allowed
def get_day_light_data(d, day_light, location_info):
    print(f"RENDER '{day.isoformat()}'!")
    astral_event = project_converters.DatetimeToSimultaneousEvent(
        location_info
    ).convert(d)
    clock_tuple, orchestration = astral_event_to_clock_tuple(astral_event)
    return (d, day_light, astral_event, clock_tuple, orchestration)


def _illustrate(
    d, day_light, astral_event, clock_tuple, orchestration, notation_path, executor
):
    project.render.illustration(orchestration, d, executor)


def notate(day_light_list, executor):
    day_light_to_notate_tuple = ("sunset",)
    future_list = []
    day_light_to_notation_path_list = {
        day_light: [] for day_light in day_light_to_notate_tuple
    }
    for data in day_light_list:
        if (day_light := data[1]) in day_light_to_notate_tuple:
            print(day_light)
            notation_path_list = day_light_to_notation_path_list[day_light]
            d = data[0]
            notation_path = f"builds/notations/{project.constants.TITLE}_{d.year}_{d.month}_{d.day}_{day_light}.pdf"
            if future := _notate(*data, notation_path, executor):
                future_list.append(future)
                notation_path_list.append(notation_path)

    while any([f.running() for f in future_list]):
        time.sleep(0.1)

    for day_light, notation_path_list in day_light_to_notation_path_list.items():
        if notation_path_list:
            project.render.merge_notation(day_light, notation_path_list)


@run_if_allowed
def _notate(
    d, day_light, astral_event, clock_tuple, orchestration, notation_path, executor
):
    print("\tnotate...")
    intonation_tuple = project.constants.MOON_PHASE_TO_INTONATION[
        astral_event["moon_phase"][0].moon_phase
    ]
    scale = music_parameters.Scale(
        music_parameters.JustIntonationPitch("1/1"),
        music_parameters.RepeatingScaleFamily(
            intonation_tuple,
            min_pitch_interval=music_parameters.JustIntonationPitch("1/16"),
            max_pitch_interval=music_parameters.JustIntonationPitch("32/1"),
        ),
    )
    return project.render.notation(
        clock_tuple, d, scale, orchestration, notation_path, executor
    )


def sound(day_light_list, executor):
    for data in day_light_list:
        _sound(*data, executor)


@run_if_allowed
def _sound(d, day_light, astral_event, clock_tuple, orchestration, executor):
    print("\tsound...")
    # For both - midi frontend and walkman frontend - we need
    # to convert our clocks to one simultaneous event. So we do
    # it here instead of having it inside the midi converter.
    clock2sim = clock_converters.ClockToSimultaneousEvent(
        project_converters.ClockLineToSimultaneousEvent()
    ).convert

    simultaneous_event = core_events.SimultaneousEvent([])
    for clock in clock_tuple:
        clock_simultaneous_event = clock2sim(clock, repetition_count=1)
        simultaneous_event.concatenate_by_tag(clock_simultaneous_event)

    # Our clock event has the tempo information, but this tempo information
    # is actually valid for the complete event! So we actually need
    # to move it to a higher layer before apply 'metrize'.
    simultaneous_event.tempo_envelope, simultaneous_event["clock"][0].tempo_envelope = (
        simultaneous_event["clock"][0].tempo_envelope,
        simultaneous_event.tempo_envelope,
    )
    simultaneous_event.metrize()

    project.render.walkman(simultaneous_event, d)

    return project.render.midi(simultaneous_event, executor)


allowed_date_list = [
    datetime.datetime(2023, 4, 1),  # moon phase index 10.61 :)
    # datetime.datetime(2023, 4, 23),
    # datetime.datetime(2023, 4, 24),
    # datetime.datetime(2023, 4, 25),
    # datetime.datetime(2023, 4, 26),
    # datetime.datetime(2023, 4, 27),
    # datetime.datetime(2023, 4, 28),
    # datetime.datetime(2023, 4, 29),
    # datetime.datetime(2023, 4, 30),  # moon phase index 9.98 :)
]
# allowed_date_list = [datetime.datetime(2023, 4, 30)]
allowed_day_light_list = [
    "sunset"
    # "dusk",
]

if __name__ == "__main__":
    # Duplicated in walkman_modules.aeolian_harp
    location_info = LocationInfo(
        name="Essen",
        region="NRW",
        timezone="Europe/Berlin",
        latitude=51.4556432,
        longitude=7.0115552,
    )

    # import logging
    # logging.setLevel(logging.DEBUG)

    with ThreadPoolExecutor(max_workers=8) as executor:
        with diary_interfaces.open():
            april = tuple(
                datetime.datetime(2023, 4, d, tzinfo=location_info.tzinfo)
                for d in range(1, 31)
            )
            day_light_list = []
            for day in april:
                s = sun.sun(
                    location_info.observer,
                    date=day,
                    dawn_dusk_depression=Depression.CIVIL,
                )
                for day_light in ("dawn", "sunrise", "sunset", "dusk"):
                    if day_light_data := get_day_light_data(
                        s[day_light], day_light, location_info
                    ):
                        day_light_list.append(day_light_data)

            notate(day_light_list, executor)
            sound(day_light_list, executor)
