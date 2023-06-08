from quicktions import Fraction as f

import numpy as np
import ranges

from mutwo import core_converters
from mutwo import clock_converters
from mutwo import clock_events
from mutwo import clock_interfaces
from mutwo import core_events
from mutwo import project_converters
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


def scale_to_markov_chain(scale):
    key = tuple(p.ratio for p in scale.scale_family.interval_tuple)
    try:
        markov_chain = _scale_to_markov_chain[key]
    except KeyError:
        gatra_tuple = scale_to_gatra_tuple.convert(scale)
        markov_chain = _scale_to_markov_chain[
            key
        ] = gatra_tuple_to_markov_chain.convert(gatra_tuple)
        markov_chain.make_deterministic_map()
    return markov_chain


def insert_modal_event(
    modal_sequential_event,
    scale,
    index: int = 3,
    energy: float = 0,
    duration: f = f(25, 16),
):
    if not (len(modal_sequential_event) > index):
        return
    assert index > 0, "Can't insert at first position"
    modal_sequential_event.insert(
        index,
        clock_events.ModalEvent0(
            modal_sequential_event[index - 1].end_pitch,
            modal_sequential_event[index - 1].end_pitch,
            scale,
            energy=energy,
            clock_event=clock_events.ClockEvent(
                [core_events.SequentialEvent([core_events.SimpleEvent(duration)])]
            ),
        ),
    )


scale_to_gatra_tuple = project_converters.ScaleToGatraTuple()
gatra_tuple_to_markov_chain = project_converters.GatraTupleToMarkovChain()
_scale_to_markov_chain = {}


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
