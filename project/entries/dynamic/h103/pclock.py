import quicktions as fractions

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_events
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert isinstance(context, diary_interfaces.H103Context)
        assert context.attr == "pclock"
    except AssertionError:
        return False
    return True


def main(
    context, random, activity_level, **kwargs
) -> timeline_interfaces.EventPlacement:

    duration = context.end - context.start

    position = 0.5
    real_duration = fractions.Fraction(1, 4)
    if real_duration > duration:
        real_duration = duration - fractions.Fraction(1, 16)

    start_range, end_range = project_utilities.get_ranges(
        real_duration, duration, position
    )

    n = music_events.NoteLike("c", 1)
    sequential_event = core_events.SequentialEvent([n])

    simultaneous_event = core_events.TaggedSimultaneousEvent(
        [sequential_event], tag=context.attr
    )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([simultaneous_event]), start_range, end_range
    ).move_by(context.start)
