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

    # Sometimes drop tones (variety), but there are some conditions:
    #
    #  1  Tonics can't be dropped.
    dropable = [context.attr != "tonic"]
    #
    #  2  It's ok to remove the more frequent notes which are only valid for
    #     1 chord, but it would be rather unfortunate to remove notes which
    #     span over multiple chords
    #
    #     (The energy parameter is mapped to how often a pitch can be repeated
    #     over different chords.)
    dropable.append(context.energy < 2)
    #  3  It is not ok to drop a not-tonic pitch, in case this is the only
    #     pitch in our chord which doesn't have a comma (this can happen
    #     if the tonic has a comma). It's not ok, because then we don't
    #     have any non-comma reference anymore.
    dropable.append(
        any(
            [
                (p.exponent_tuple[2] if len(p.exponent_tuple) > 2 else 0) == 0
                for p in context.other_pitch_tuple
            ]
        )
    )
    if all(dropable) and activity_level(4):
        return

    # First the reference tones which are easier to intonate, and then
    # we add up the more complex intonations.
    match context.attr:
        case "tonic":
            position = 0.25
            duration_diff = fractions.Fraction(1, 8)
            volume = music_parameters.DecibelVolume(-35.75)
        case "partner":
            position = 0.5
            duration_diff = fractions.Fraction(1, 4)
            volume = music_parameters.DecibelVolume(-36)
        case _:
            position = 0.75
            duration_diff = fractions.Fraction(1, 2)
            volume = music_parameters.DecibelVolume(-35.5)

    duration = context.end - context.start

    while duration_diff > duration:
        duration_diff -= fractions.Fraction(1, 16)

    real_duration = duration - duration_diff

    start_range, end_range = project_utilities.get_ranges(
        real_duration, duration, position
    )

    n = music_events.NoteLike(
        AMBITUS.get_pitch_variant_tuple(context.pitch)[0], 1, volume=volume
    )
    n.notation_indicator_collection.duration_line.is_active = True
    sequential_event = core_events.SequentialEvent([n])

    match context.attr:
        case "tonic":
            pass
        case "partner":
            pass
        case _:
            # If we have instable pitches, they can either be a
            # minor or a major interval. We show this to others by
            # adding parenthesis to the accidental (= can be added, but
            # doesn't need to).
            # But we only do so in case we have a flat/sharp accidental,
            # otherwise it's not clear what the pitch should sound like
            # without the accidental.
            if len(n.pitch_list[0].get_closest_pythagorean_pitch_name()) != 1:
                n.playing_indicator_collection.optional_accidental.is_active = True

    simultaneous_event = core_events.TaggedSimultaneousEvent(
        [sequential_event], tag=context.attr
    )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([simultaneous_event]), start_range, end_range
    ).move_by(context.start)


AMBITUS = music_parameters.OctaveAmbitus(
    # e' to e''
    #
    # In this way we don't need to print any lines out of the system :)
    # So it's easier to read for everyone & we can avoid some signs.
    music_parameters.JustIntonationPitch("3/4"),
    music_parameters.JustIntonationPitch("3/2"),
)
