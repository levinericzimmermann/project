import quicktions as fractions

import numpy as np
import ranges

from mutwo import clock_events
from mutwo import core_events


def apply_clock_events(
    modal_0_sequential_event: core_events.SequentialEvent[clock_events.ModalEvent0],
):
    random = np.random.default_rng(seed=1)
    filtered_seq = tuple(
        filter(
            lambda e: isinstance(e, clock_events.ModalEvent0), modal_0_sequential_event
        )
    )
    clock_event_list = []
    for index, modal_event_0 in enumerate(filtered_seq):
        duration = index_to_duration(index, random)
        clock_event = clock_events.ClockEvent(
            [core_events.SequentialEvent([core_events.SimpleEvent(duration)])]
        )
        clock_event_list.append(clock_event)
    for modal_event0, clock_event in zip(filtered_seq, clock_event_list):
        modal_event0.clock_event = clock_event
        # dummy event
        modal_event0.control_event = core_events.SequentialEvent(
            [core_events.SimpleEvent(1)]
        )


def index_to_duration(index, random):
    duration_range = index_to_duration_range(index)
    return fractions.Fraction(
        # Explicit cast to builtin int to avoid later
        # problems with abjad which can only handle builtin
        # int and not numpy int.
        int(random.integers(duration_range.start, duration_range.end)), 16
    )


def index_to_duration_range(index):
    r = ranges.Range
    match index % 4:
        case 0:
            return r(20, 35)
        case 1:
            return r(30, 55)
        case 2:
            return r(20, 35)
        case 3:
            return r(65, 95)
        case _:
            raise RuntimeError()
