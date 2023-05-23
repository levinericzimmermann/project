import fractions

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_events
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, pitch=None, **kwargs):
    try:
        assert context.modal_event.pitch is not None
        assert isinstance(context.modal_event, clock_events.ModalEvent1)
        orchestration = context.orchestration
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert isinstance(instrument, music_parameters.abc.PitchedInstrument)
        assert instrument.name in ("glockenspiel",)
        pitch = pitch or get_pitch(context)
        assert instrument.get_pitch_variant_tuple(pitch)
        assert context.index != 0
    except AssertionError:
        return False
    return True


def main(
    context, random, activity_level, pitch=None, **kwargs
) -> timeline_interfaces.EventPlacement:
    orchestration = context.orchestration
    instrument = orchestration[0]
    scale = context.modal_event.scale
    pitch = pitch or get_pitch(context)
    pitch_tuple = instrument.get_pitch_variant_tuple(pitch)

    sequential_event = core_events.SequentialEvent([])

    is_first = True
    for _ in range(random.choice([1, 2, 3])):
        if not is_first:
            rest = core_events.SimpleEvent(duration=0.25)
            sequential_event.append(rest)
        else:
            is_first = False
        note = music_events.NoteLike(random.choice(pitch_tuple), 1, volume="pp")
        note.notation_indicator_collection.duration_line.is_active = True
        sequential_event.append(note)

    simultaneous_event = project_events.SimultaneousEventWithRepetition(
        [
            project_events.TaggedSimultaneousEventWithRepetition(
                [sequential_event],
                tag=instrument.name,
            )
        ]
    )

    duration = context.modal_event.clock_event.duration

    real_duration = fractions.Fraction(30, 16)
    if real_duration > duration:
        real_duration = duration
    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


def get_pitch(context):
    return context.modal_event.pitch
