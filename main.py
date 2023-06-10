from quicktions import Fraction as f

import numpy as np
import ranges

from mutwo import clock_events
from mutwo import clock_interfaces
from mutwo import core_events
from mutwo import diary_converters
from mutwo import project_converters
from mutwo import timeline_interfaces

import project

c103_sequential_event_to_context_tuple = (
    project_converters.C103SequentialEventToContextTuple()
)
context_tuple_to_event_placement_tuple = (
    diary_converters.ContextTupleToEventPlacementTuple()
)


def make_clock(week_day, before_rest_duration=0) -> clock_interfaces.Clock:
    if week_day in (project.constants.WeekDay.MONDAY, project.constants.WeekDay.SUNDAY):
        return clock_interfaces.Clock(_clock_rest(1))

    tonic_movement_tuple = project.constants.WEEK_DAY_TO_TONIC_MOVEMENT_TUPLE[week_day]

    tonic_movement_tuple_to_c103_sequential_event = (
        project_converters.TonicMovementTupleToC103SequentialEvent()
    )

    c103_sequential_event = tonic_movement_tuple_to_c103_sequential_event(
        tonic_movement_tuple
    )
    context_tuple = c103_sequential_event_to_context_tuple(c103_sequential_event)
    event_placement_tuple = context_tuple_to_event_placement_tuple(context_tuple)

    clock_event = clock_events.ClockEvent(
        [
            core_events.SequentialEvent(
                [core_events.SimpleEvent(c103_sequential_event.duration)]
            )
        ]
    )

    main_clock_line = clock_interfaces.ClockLine(clock_event=clock_event)
    for ep in event_placement_tuple:
        main_clock_line.register(ep)

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


def _clock_rest(rest_duration):
    return clock_interfaces.ClockLine(
        clock_events.ClockEvent(
            [core_events.SequentialEvent([core_events.SimpleEvent(rest_duration)])]
        )
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="project")
    parser.add_argument("-i", "--illustration", action="store_true")
    parser.add_argument("-n", "--notation", action="store_true")
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
        for i, week_day in enumerate(project.constants.WeekDay):
            if i >= max_index:
                break
            clock_list.append(make_clock(week_day))

    clock_tuple = tuple(clock_list)

    if args.notation:
        project.render.notation(clock_tuple, [])

    if args.sound:
        project.render.midi(clock_tuple)
