from quicktions import Fraction as f

import numpy as np
import ranges

from mutwo import core_converters
from mutwo import clock_converters
from mutwo import clock_events
from mutwo import clock_interfaces
from mutwo import core_events
from mutwo import diary_converters
from mutwo import project_converters
from mutwo import timeline_interfaces

import project


def make_clock(poem_index, poem_line, before_rest_duration=0) -> clock_interfaces.Clock:
    print("make clock for", poem_line, "...")

    scale = project.constants.PENTATONIC_SCALE_TUPLE[poem_index]

    part_count = project.constants.GATRA_COUNT
    if not poem_line:
        scale_position_tuple = tuple((0, 0) for _ in range(part_count))
    else:
        markov_chain = scale_to_markov_chain(scale)
        g = markov_chain.walk_deterministic(tuple(markov_chain.keys())[0])

        scale_position_list = []
        for _ in range(part_count):
            scale_position_list.extend(next(g))

        scale_position_tuple = tuple(scale_position_list)

    root_pitch_tuple = tuple(
        scale.scale_position_to_pitch(scale_position)
        for scale_position in scale_position_tuple
    )

    modal_sequential_event = core_events.SequentialEvent(
        [
            clock_events.ModalEvent0(start_pitch, end_pitch, scale)
            for start_pitch, end_pitch in zip(root_pitch_tuple, root_pitch_tuple[1:])
        ]
    )

    project.clocks.apply_clock_events(modal_sequential_event)

    for modal_event in modal_sequential_event:
        modal_event.control_event = core_events.SimultaneousEvent(
            [core_events.SequentialEvent([core_events.SimpleEvent(1)])]
        )

    main_clock_line = clock_converters.Modal0SequentialEventToClockLine(
        (
            diary_converters.Modal0SequentialEventToEventPlacementTuple(
                orchestration=project.constants.ORCHESTRATION.get_subset("PCLOCK"),
                add_mod1=True,
            ),
            diary_converters.Modal0SequentialEventToEventPlacementTuple(
                orchestration=project.constants.ORCHESTRATION.get_subset(
                    "GLOCKENSPIEL"
                ),
                add_mod1=True,
            ),
            diary_converters.Modal0SequentialEventToEventPlacementTuple(
                orchestration=project.constants.ORCHESTRATION.get_subset("HARP"),
                add_mod1=False,
            ),
            diary_converters.Modal0SequentialEventToEventPlacementTuple(
                orchestration=project.constants.ORCHESTRATION.get_subset("V"),
                add_mod1=True,
            ),
            diary_converters.Modal0SequentialEventToEventPlacementTuple(
                orchestration=project.constants.ORCHESTRATION.get_subset(
                    "V", "HARP", "GLOCKENSPIEL"
                ),
                add_mod1=False,
            ),
        )
    ).convert(modal_sequential_event)

    # Fix overlaps
    main_clock_line.resolve_conflicts([timeline_interfaces.AlternatingStrategy()])

    start_clock_line = (
        _clock_rest(before_rest_duration) if before_rest_duration > 0 else None
    )
    end_clock_line = _clock_end(scale)
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


scale_to_gatra_tuple = project_converters.ScaleToGatraTuple()
gatra_tuple_to_markov_chain = project_converters.GatraTupleToMarkovChain()
_scale_to_markov_chain = {}


def _clock_rest(rest_duration):
    return clock_interfaces.ClockLine(
        clock_events.ClockEvent(
            [core_events.SequentialEvent([core_events.SimpleEvent(rest_duration)])]
        )
    )


def _clock_end(scale):
    modal_sequential_event = core_events.SequentialEvent(
        [
            clock_events.ModalEvent0(
                scale.scale_index_to_pitch(0), scale.scale_index_to_pitch(0), scale
            ).set("is_end", True)
        ]
    )
    project.clocks.apply_clock_events(modal_sequential_event)
    return clock_converters.Modal0SequentialEventToClockLine([]).convert(
        modal_sequential_event
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="project")
    parser.add_argument("-i", "--illustration", action="store_true")
    parser.add_argument("-n", "--notation", default="all")
    parser.add_argument("-s", "--sound", action="store_true")
    parser.add_argument("-m", "--max-index", default=16)

    args = parser.parse_args()
    max_index = int(args.max_index)

    if args.illustration:
        project.render.illustration()

    from mutwo import diary_interfaces

    with diary_interfaces.open():
        clock_list = []
        for index, line in enumerate(project.constants.POEM.split("\n")):
            if index < max_index:
                clock_list.append(make_clock(index, line))
            else:
                break

    clock_tuple = tuple(clock_list)

    if args.notation:
        project.render.notation(clock_tuple, args.notation)

    if args.sound:
        project.render.midi(clock_tuple)
