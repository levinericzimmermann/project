import ranges

from mutwo import core_events
from mutwo import clock_events
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import timeline_interfaces


def is_supported(context, tremolo_middle=None, **kwargs):
    try:
        assert isinstance(context, diary_interfaces.ModalContext1)
        assert isinstance(context.modal_event, clock_events.ModalEvent1)
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
        case 1:
            clock_event = tremolo_middle(instrument_index_tuple=[4], **kwargs)
        case 2:
            clock_event = grace(**kwargs)
        case 3:
            clock_event = tremolo_long(
                instrument_index_tuple=[2], **kwargs
            ).concatenate_by_index(
                hit(instrument_index_tuple=[random.choice((2, 3, 4))], **kwargs)
            )
        case _:
            raise RuntimeError()

    duration = context.modal_event.clock_event.duration
    start_range = ranges.Range(duration * 0.05, duration * 0.1)
    end_range = ranges.Range(duration * 0.95, duration * 0.985)

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([clock_event]), start_range, end_range
    ).move_by(context.start)
