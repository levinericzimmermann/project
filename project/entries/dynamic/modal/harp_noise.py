import fractions

from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert context.energy >= 40 and context.energy <= 60
        assert len(context.orchestration) == 1
        assert isinstance(context_to_instrument(context), music_parameters.CelticHarp)
    except AssertionError:
        return False
    return True


def main(context, activity_level, **kwargs) -> timeline_interfaces.EventPlacement:
    orchestration = context.orchestration

    duration = context.modal_event.clock_event.duration

    real_duration = fractions.Fraction(30, 16)
    if real_duration > duration:
        real_duration = duration - fractions.Fraction(2, 16)
    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.95)

    simultaneous_event = core_events.SimultaneousEvent([])
    for instrument in orchestration:
        tagged_simultaneous_event = core_events.TaggedSimultaneousEvent(
            [], tag=instrument.name
        )

        for activate in (
            lambda n: setattr(
                n.playing_indicator_collection.harp_superball, "is_active", 1
            ),
            lambda n: setattr(n.notation_indicator_collection.hide, "is_active", 1),
        ):
            note_like = music_events.NoteLike("c", duration=1)
            activate(note_like)
            sequential_event = core_events.SequentialEvent([note_like])
            tagged_simultaneous_event.append(sequential_event)
        simultaneous_event.append(tagged_simultaneous_event)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


def context_to_instrument(context):
    orchestration = context.orchestration
    return orchestration[0]
