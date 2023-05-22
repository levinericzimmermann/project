import fractions

import ranges

from mutwo import core_events
from mutwo import clock_events
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, tremolo_middle=None, **kwargs):
    try:
        assert isinstance(context, diary_interfaces.ModalContext1)
        assert isinstance(context.modal_event, clock_events.ModalEvent1)
        assert context.modal_event.pitch is not None
        orchestration = context.orchestration
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert isinstance(instrument, music_parameters.UnpitchedInstrument)
    except AssertionError:
        return False
    return True


def main(context, tremolo_middle, tremolo_long, grace, hit, random, **kwargs):

    match context.index % 4:
        case 0:
            clock_event = hit(
                instrument_index_tuple=[random.choice((2, 3, 4))], **kwargs
            )
            position = 0
            real_duration = fractions.Fraction(10, 16)
        case 1:
            clock_event = tremolo_middle(instrument_index_tuple=[4], **kwargs)
            position = 0.1
            real_duration = fractions.Fraction(21, 16)
        case 2:
            clock_event = grace(**kwargs)
            position = 0.25
            real_duration = fractions.Fraction(12, 16)
        case 3:
            clock_event = tremolo_long(
                instrument_index_tuple=[2], **kwargs
            ).concatenate_by_index(
                hit(instrument_index_tuple=[random.choice((2, 3, 4))], **kwargs)
            )
            position = 0.85
            real_duration = fractions.Fraction(25, 16)
        case _:
            raise RuntimeError()

    duration = context.modal_event.clock_event.duration
    if real_duration > duration:
        real_duration = duration - fractions.Fraction(1, 16)

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, position)

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([clock_event]), start_range, end_range
    ).move_by(context.start)
