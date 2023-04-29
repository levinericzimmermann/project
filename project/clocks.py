from quicktions import Fraction as f

import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import core_parameters


def apply_clock_events(
    modal_0_sequential_event: core_events.SequentialEvent[clock_events.ModalEvent0],
):
    filtered_seq = tuple(
        filter(
            lambda e: isinstance(e, clock_events.ModalEvent0), modal_0_sequential_event
        )
    )
    d = core_parameters.DirectDuration
    clock_event_list = []
    for modal_event_0 in filtered_seq:
        if getattr(modal_event_0, "is_end", False):
            duration_range = ranges.Range(d(f(10, 16)), d(f(30, 16)))
        else:
            duration_range = ranges.Range(d(f(30, 16)), d(f(60, 16)))
        clock_event = clock_events.ClockEvent(
            [core_events.SequentialEvent([core_events.SimpleEvent(duration_range.end)])]
        )
        clock_event_list.append(clock_event)
    for modal_event0, clock_event in zip(filtered_seq, clock_event_list):
        modal_event0.clock_event = clock_event
        # dummy event
        modal_event0.control_event = core_events.SequentialEvent(
            [core_events.SimpleEvent(1)]
        )
