import fractions

from mutwo import core_events
from mutwo import music_events
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert context.energy < 0
    except AssertionError:
        return False
    return True


def main(context, **kwargs) -> timeline_interfaces.EventPlacement:
    orchestration = context.orchestration

    duration = context.modal_event.clock_event.duration

    real_duration = fractions.Fraction(10, 16)
    if real_duration > duration:
        real_duration = duration
    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

    simultaneous_event = core_events.SimultaneousEvent([])
    for instrument in orchestration:
        note_like = music_events.NoteLike(duration=1)
        # Any of
        #
        #   "shortfermata",
        #   "fermata",
        #   "longfermata",
        #   "verylongfermata",
        #
        note_like.playing_indicator_collection.fermata.type = "longfermata"
        sequential_event = core_events.SequentialEvent([note_like])
        tagged_simultaneous_event = core_events.TaggedSimultaneousEvent(
            [sequential_event], tag=instrument.name
        )
        simultaneous_event.append(tagged_simultaneous_event)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)
