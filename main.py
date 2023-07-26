from quicktions import Fraction as f

import numpy as np
import ranges

from mutwo import core_converters
from mutwo import clock_converters
from mutwo import clock_interfaces
from mutwo import core_events
from mutwo import timeline_interfaces

import project


def make_clock(before_rest_duration=0) -> clock_interfaces.Clock:
    modal_sequential_event = core_events.SequentialEvent([])

    project.clocks.apply_clock_events(modal_sequential_event)

    for modal_event in modal_sequential_event:
        modal_event.control_event = core_events.SimultaneousEvent(
            [core_events.SequentialEvent([core_events.SimpleEvent(1)])]
        )

    main_clock_line = clock_converters.Modal0SequentialEventToClockLine(()).convert(
        modal_sequential_event
    )

    # Fix overlaps
    main_clock_line.resolve_conflicts(
        [
            timeline_interfaces.AlternatingStrategy(),
        ],
    )

    start_clock_line = None
    end_clock_line = None
    clock = clock_interfaces.Clock(main_clock_line, start_clock_line, end_clock_line)

    return clock


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="project")
    parser.add_argument("-i", "--illustration", action="store_true")
    parser.add_argument("-n", "--notation", default="")
    parser.add_argument("-s", "--sound", action="store_true")
    parser.add_argument("-m", "--max-index", default=16)

    args = parser.parse_args()
    max_index = int(args.max_index)

    if args.illustration:
        project.render.illustration()

    # import logging
    # from mutwo import diary_converters
    # diary_converters.configurations.LOGGING_LEVEL = logging.DEBUG

    from mutwo import diary_interfaces

    with diary_interfaces.open():
        clock_list = []
        for _ in range(1):
            clock_list.append(make_clock())

    clock_tuple = tuple(clock_list)

    if args.notation:
        project.render.notation(clock_tuple, args.notation)

    if args.sound:
        project.render.midi(clock_tuple)
