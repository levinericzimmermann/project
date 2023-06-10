import quicktions as fractions

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_events
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert isinstance(context, diary_interfaces.H103Context)
    except AssertionError:
        return False
    return True


def main(
    context, random, activity_level, **kwargs
) -> timeline_interfaces.EventPlacement:
    duration = context.end - context.start

    real_duration = fractions.Fraction(22, 16)
    if real_duration > duration:
        real_duration = duration - fractions.Fraction(1, 16)

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

    sequential_event = core_events.SequentialEvent(
        [music_events.NoteLike(context.pitch, 1)]
    )

    simultaneous_event = core_events.TaggedSimultaneousEvent(
        [sequential_event], tag=context.attr
    )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([simultaneous_event]), start_range, end_range
    ).move_by(context.start)
