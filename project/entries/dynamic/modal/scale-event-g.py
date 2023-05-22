import quicktions as fractions

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_events
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert isinstance(context, diary_interfaces.ModalContext0)
        assert context.modal_event.start_pitch != context.modal_event.end_pitch
        orchestration = context.orchestration
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert instrument.name in ("glockenspiel",)
    except AssertionError:
        return False
    return True


def main(
    context, random, activity_level, scale, **kwargs
) -> timeline_interfaces.EventPlacement:
    modal_event_to_convert = context.modal_event
    instrument = context.orchestration[0]
    duration = modal_event_to_convert.clock_event.duration

    real_duration = fractions.Fraction(22, 16)
    if real_duration > duration:
        real_duration = duration

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

    pitch_tuple_list = []
    for direction in (True, False):
        pitch_tuple = scale(context, direction=direction, octave_count=0, **kwargs)
        pitch_tuple_list.append((len(pitch_tuple), pitch_tuple))

    pitch_tuple = max(pitch_tuple_list, key=lambda p: p[0])[1]

    sequential_event = core_events.SequentialEvent([])
    for p in pitch_tuple:
        n = music_events.NoteLike(p, 1, 'ppp')
        sequential_event.append(n)

    if len(sequential_event) < 4:
        for n in sequential_event:
            n.notation_indicator_collection.duration_line.is_active = True

    simultaneous_event = core_events.TaggedSimultaneousEvent(
        [sequential_event], tag=instrument.name
    )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([simultaneous_event]), start_range, end_range
    ).move_by(context.start)


def duration_to_event_count(duration):
    return int(duration / density[0]) * density[1]


density = (fractions.Fraction(9, 16), 1)
