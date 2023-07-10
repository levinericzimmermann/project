from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_events
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert isinstance(context, diary_interfaces.H103Context)
        assert context.attr != "pclock"
        assert context.pitch is None
    except AssertionError:
        return False
    return True


def main(
    context, random, activity_level, **kwargs
) -> timeline_interfaces.EventPlacement:
    duration = context.end - context.start
    real_duration = duration

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

    n = music_events.NoteLike(duration=1)
    n.is_noise = context.is_noise
    n.is_generalpause = context.is_generalpause
    simultaneous_event = core_events.TaggedSimultaneousEvent(
        [core_events.SequentialEvent([n])], tag=context.attr
    )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([simultaneous_event]), start_range, end_range
    ).move_by(context.start)
