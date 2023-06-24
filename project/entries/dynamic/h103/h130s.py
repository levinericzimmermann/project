import quicktions as fractions

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert isinstance(context, diary_interfaces.H103Context)
        assert context.attr != "pclock"
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

    # First the reference tones which are easier to intonate, and then
    # we add up the more complex intonations.
    match context.attr:
        case "tonic":
            position = 0.25
            duration_diff = fractions.Fraction(1, 8)
            volume = music_parameters.DecibelVolume(-37)
        case "partner":
            position = 0.5
            duration_diff = fractions.Fraction(1, 4)
            volume = music_parameters.DecibelVolume(-37)
        case _:
            position = 0.75
            duration_diff = fractions.Fraction(1, 2)
            volume = music_parameters.DecibelVolume(-37)

    duration = context.end - context.start

    while duration_diff > duration:
        duration_diff -= fractions.Fraction(1, 16)

    real_duration = duration - duration_diff

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, position)

    n = music_events.NoteLike(context.pitch, 1, volume=volume)
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
