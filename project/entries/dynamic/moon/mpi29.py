import ranges

from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_events
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert int(context.moon_phase_index) in (29,)
        assert hasattr(context.orchestration, "AEOLIAN_HARP")
    except AssertionError:
        return False
    return True


def main(
    context, activity_level, random, **kwargs
) -> timeline_interfaces.EventPlacement:
    aeolian_harp = context.orchestration.AEOLIAN_HARP
    duration = context.end - context.start

    simultaneous_event = core_events.TaggedSimultaneousEvent(tag=aeolian_harp.name)
    for string in aeolian_harp.string_tuple:
        print(string)
        simultaneous_event.append(
            make_sequential_event(
                string, duration, random.choice((7, 8, 9)), activity_level, random
            )
        )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([simultaneous_event]),
        context.start,
        context.end,
    )


def make_sequential_event(string, duration, level, activity_level, random):
    duration_range_tuple = (ranges.Range(4, 12), ranges.Range(40, 60))

    sequential_event = core_events.SequentialEvent([])
    seqd = core_parameters.DirectDuration(0)
    while seqd < duration:
        note_like = music_events.NoteLike()
        if is_active := activity_level(level):
            note_like.pitch_list = [string.tuning]
            note_like.envelope = random.choice(
                ["BASIC", "BASIC_QUIET", "PLUCK_0", "PLUCK_1"]
            )
            note_like.frequency_factor = random.uniform(0.07, 0.1)

        duration_range = duration_range_tuple[is_active]
        note_like.duration = random.uniform(duration_range.start, duration_range.end)
        sequential_event.append(note_like)
        seqd += note_like.duration

    return sequential_event.set("duration", duration)
