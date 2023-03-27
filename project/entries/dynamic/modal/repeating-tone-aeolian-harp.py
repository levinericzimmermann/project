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


def is_supported(context, **kwargs):
    try:
        assert hasattr(context, "orchestration")
        assert len(context.orchestration) == 1
        instrument = context.orchestration[0]
        assert isinstance(instrument, project_parameters.AeolianHarp)
        assert context.energy < 4
    except AssertionError:
        return False
    return True


def main(
    context,
    random,
    activity_level,
    event_count_to_average_tone_duration={6: 12, 4: 15},
    **kwargs,
) -> timeline_interfaces.EventPlacement:
    modal_event_to_convert = context.modal_event
    instrument = context.orchestration[0]

    event_count = random.choice([6, 4])

    start_range, end_range = make_range_pair(
        event_count, event_count_to_average_tone_duration, modal_event_to_convert
    )

    pitch = instrument.get_pitch_variant_tuple(modal_event_to_convert.end_pitch)[0]
    string_tuple = tuple(s for s in instrument.string_tuple if s.tuning == pitch)

    sim = make_simultaneous_event(
        string_tuple, random, instrument, activity_level, event_count
    )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([sim]),
        start_range,
        end_range,
    ).move_by(context.start)


def make_range_pair(
    event_count, event_count_to_average_tone_duration, modal_event_to_convert
):

    duration_in_seconds = modal_event_to_convert.clock_event.metrize(
        mutate=False
    ).duration.duration_in_floats

    average_tone_duration_in_seconds = event_count_to_average_tone_duration[event_count]
    duration = modal_event_to_convert.clock_event.duration

    return project_converters.AverageNoteDurationToRangePair().convert(
        average_tone_duration_in_seconds, event_count, duration_in_seconds, duration
    )


def make_simultaneous_event(
    string_tuple, random, instrument, activity_level, event_count
):
    tag = instrument.name

    duration_list = [
        1 if i % 2 == 0 else random.choice([0.5, 0.75]) for i in range(event_count)
    ]
    summed_duration = sum(duration_list)

    sim = core_events.TaggedSimultaneousEvent(
        [
            core_events.SequentialEvent([core_events.SimpleEvent(summed_duration)])
            for _ in range(instrument.TOTAL_STRING_COUNT)
        ],
        tag=tag,
    )

    envelope = "BASIC_QUIET"
    frequency_factor = 1 / 4

    absolute_time = core_parameters.DirectDuration(0)
    for index, duration, start in zip(
        range(event_count),
        duration_list,
        core_utilities.accumulate_from_zero(duration_list),
    ):
        if index % 2 == 0:
            for string in string_tuple:
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
