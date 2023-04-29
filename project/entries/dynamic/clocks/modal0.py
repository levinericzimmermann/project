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


def main(context, tremolo_middle=None, **kwargs):
    clock_event = tremolo_middle(instrument_index_tuple=[3], **kwargs)

    duration = context.modal_event.clock_event.duration
    start_range = ranges.Range(duration * 0.05, duration * 0.1)
    end_range = ranges.Range(duration * 0.95, duration * 0.985)

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([clock_event]), start_range, end_range
    ).move_by(context.start)
