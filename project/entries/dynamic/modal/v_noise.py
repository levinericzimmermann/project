import fractions

from mutwo import core_events
from mutwo import music_events
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        # assert context.energy < 50
        orchestration = context.orchestration
        assert len(orchestration) == 1
        assert orchestration[0].name == "v"
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

        note_like = music_events.NoteLike("c", duration=1)
        pic = note_like.playing_indicator_collection
        if activity_level(7):
            pic.bridge.is_active = True
        else:
            pic.moving_overpressure.is_active = True
        sequential_event = core_events.SequentialEvent([note_like])
        tagged_simultaneous_event.append(sequential_event)
        simultaneous_event.append(tagged_simultaneous_event)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)
