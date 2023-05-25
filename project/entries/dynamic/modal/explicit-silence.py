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

    real_duration = fractions.Fraction(20, 16)
    if real_duration > duration:
        real_duration = duration - fractions.Fraction(2, 16)
    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.95)

    simultaneous_event = core_events.SimultaneousEvent([])
    for instrument in orchestration:
        if instrument.name == "pclock":
            continue

        tagged_simultaneous_event = core_events.TaggedSimultaneousEvent(
            [], tag=instrument.name
        )

        match instrument.name:
            case "harp":
                staff_count = 2
            case _:
                staff_count = 1

        for _ in range(staff_count):
            note_like = music_events.NoteLike(duration=1)
            try:
                fermata_type = FERMATA_TYPE_TUPLE[abs(context.energy) - 1]
            except IndexError:
                fermata_type = FERMATA_TYPE_TUPLE[-1]
            note_like.playing_indicator_collection.fermata.type = fermata_type
            sequential_event = core_events.SequentialEvent([note_like])
            tagged_simultaneous_event.append(sequential_event)

        assert tagged_simultaneous_event

        simultaneous_event.append(tagged_simultaneous_event)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


FERMATA_TYPE_TUPLE = (
    "shortfermata",
    "fermata",
    "longfermata",
    "verylongfermata",
)
