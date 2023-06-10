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

    # The energy parameter is mapped to how often a pitch can be repeated
    # over different chords. (It's ok to remove the more frequent notes
    # which are only valid for 1 chord, but it would be rather unfortunate
    # to remove notes which span over multiple chords).
    energy = context.energy
    # Sometimes drop tones if they aren't the tonic & don't span over
    # multiple chords.
    if energy < 2 and context.attr != "tonic" and activity_level(4):
        return

    duration = context.end - context.start
    real_duration = duration - fractions.Fraction(1, 4)
    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

    n = music_events.NoteLike(context.pitch, 1)
    n.notation_indicator_collection.duration_line.is_active = True
    sequential_event = core_events.SequentialEvent(
        [n]
    )

    simultaneous_event = core_events.TaggedSimultaneousEvent(
        [sequential_event], tag=context.attr
    )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([simultaneous_event]), start_range, end_range
    ).move_by(context.start)
