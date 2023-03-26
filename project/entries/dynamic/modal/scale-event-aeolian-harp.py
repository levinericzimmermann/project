import warnings

import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_converters
from mutwo import project_parameters
from mutwo import timeline_interfaces


def is_supported(context, scale, **kwargs):
    try:
        assert hasattr(context, "orchestration")
        assert len(context.orchestration) == 1
        instrument = context.orchestration[0]
        assert isinstance(instrument, project_parameters.AeolianHarp)
    except AssertionError:
        return False
    return scale.is_supported(context, **kwargs)


def main(
    context,
    random,
    activity_level,
    scale,
    event_count_to_average_tone_duration={
        1: 21,
        2: 19.85,
        3: 17.5,
        4: 15,
        5: 14,
    },
    **kwargs,
) -> timeline_interfaces.EventPlacement:
    pitch_tuple = scale(context, **kwargs)
    modal_event_to_convert = context.modal_event
    instrument = context.orchestration[0]
    add_partner = activity_level(7)
    string_list_tuple = find_string_list_tuple(
        pitch_tuple, instrument, random, add_partner
    )

    start_range, end_range = make_range_pair(
        string_list_tuple, event_count_to_average_tone_duration, modal_event_to_convert
    )

    sim = make_simultaneous_event(string_list_tuple, random, instrument, activity_level)

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([sim]),
        start_range,
        end_range,
    ).move_by(context.start)


def make_range_pair(
    string_list_tuple, event_count_to_average_tone_duration, modal_event_to_convert
):
    event_count = len(string_list_tuple)

    duration_in_seconds = modal_event_to_convert.clock_event.metrize(
        mutate=False
    ).duration.duration_in_floats

    try:
        average_tone_duration_in_seconds = event_count_to_average_tone_duration[
            event_count
        ]
    except KeyError:
        average_tone_duration_in_seconds = 10
    duration = modal_event_to_convert.clock_event.duration

    return project_converters.AverageNoteDurationToRangePair().convert(
        average_tone_duration_in_seconds, event_count, duration_in_seconds, duration
    )


def make_simultaneous_event(string_list_tuple, random, instrument, activity_level):
    tag = instrument.name

    event_count = len(string_list_tuple)
    duration_list = [random.choice([1.75, 1.5, 2.0, 2.25, 3.25, 3]) for _ in range(event_count)]
    match random.integers(0, 3):
        case 1:
            duration_list[-1] *= 2
        case 2:
            duration_list[-1] *= 1.5
    summed_duration = sum(duration_list)

    sim = core_events.TaggedSimultaneousEvent(
        [
            core_events.SequentialEvent([core_events.SimpleEvent(summed_duration)])
            for _ in range(instrument.TOTAL_STRING_COUNT)
        ],
        tag=tag,
    )

    if activity_level(6):
        if activity_level(4):
            envelope = "BASIC"
        else:
            envelope = "BASIC_QUIET"
    else:
        if activity_level(5):
            envelope = "PLUCK_1"
        else:
            envelope = "PLUCK_0"

    frequency_factor = 1
    if envelope in ("BASIC", "BASIC_LOUD", "BASIC_QUIET"):
        frequency_factor = random.choice([0.5, 0.25])
    if envelope in ("PLUCK_0", "PLUCK_1"):
        if activity_level(3):
            frequency_factor = 2

    absolute_time = core_parameters.DirectDuration(0)
    for string_list, duration, start in zip(
        string_list_tuple,
        duration_list,
        core_utilities.accumulate_from_zero(duration_list),
    ):
        for string in string_list:
            seq = sim[string.index]
            note_like = music_events.NoteLike(
                string.tuning, duration=duration, volume="p"
            )
            note_like.frequency_factor = frequency_factor
            note_like.envelope = envelope
            seq.squash_in(start, note_like)
        absolute_time += duration

    sim.extend_until()
    return sim


def find_string_list_tuple(
    pitch_tuple, instrument, random, add_partner
) -> tuple[list[music_parameters.String], ...]:
    string_list_list = []
    for pitch in pitch_tuple:
        picked_string_list = []
        for sindex, string in enumerate(instrument.string_tuple):
            if string.tuning == pitch:
                picked_string_list.append(string)
        string_count = len(picked_string_list)
        if add_partner:
            match string_count:
                case 0:
                    warnings.warn(f"{__name__}: found no string for pitch {pitch}")
                case 1:
                    picked_string_list.append(
                        find_partner(pitch, picked_string_list[0], instrument, random)
                    )
        string_list_list.append(picked_string_list)
    return tuple(string_list_list)


def find_partner(pitch, string0, instrument, random):
    def string_index2box_index(string_index):
        return string_index // instrument.BOX_COUNT

    string0_box_index = string_index2box_index(string0.index)

    # We only pick a second string from a box which is not the same box
    # as the string which we already picked (we want to have a better
    # room effect).
    #
    # We do NOT care if the string belongs to our current scale. It's
    # ok to pick an optional pitch here.
    fitness, champion = 0, None
    for string in instrument.string_tuple:
        if string_index2box_index(string.index) != string0_box_index:
            interval = string0.tuning - string.tuning
            harmonicity = interval.harmonicity_simplified_barlow
            # Add random imprecision, so we don't necessarily always pick
            # the same partner.
            harmonicity *= random.uniform(0.5, 1)
            if champion is None or harmonicity > fitness:
                fitness, champion = harmonicity, string

    return champion
