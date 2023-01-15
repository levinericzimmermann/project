from quicktions import Fraction as f

import numpy as np
import ranges

from mutwo import core_converters
from mutwo import clock_converters
from mutwo import clock_events
from mutwo import clock_interfaces
from mutwo import core_events
from mutwo import diary_converters
from mutwo import music_events

import project


def make_clock(
    scale_position_tuple,
    before_rest_duration=0,
) -> clock_interfaces.Clock:
    scale = project.constants.SCALE

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

    # modal_sequential_event.insert(1, core_events.SimpleEvent(f(30, 16)))
    # n = music_events.NoteLike(duration=f(10, 16))
    # n.playing_indicator_collection.fermata.type = "long"
    # modal_sequential_event.insert(1, n)

    # modal_sequential_event = clock_converters.ApplyClockTreeOnModalEvent0(
    #     project.clock_trees.ModalEvent0ToClockTree(scale)
    # ).convert(modal_sequential_event)

    project.clocks.apply_clock_events(modal_sequential_event)

    main_clock_line = clock_converters.Modal0SequentialEventToClockLine(
        (
            diary_converters.Modal0SequentialEventToEventPlacementTuple(
                project.constants.ORCHESTRATION.get_subset("HARP")
            ),
            diary_converters.Modal0SequentialEventToEventPlacementTuple(
                project.constants.ORCHESTRATION.get_subset("VIOLIN")
            ),
        )
    ).convert(modal_sequential_event)

    start_clock_line = (
        _clock_rest(before_rest_duration) if before_rest_duration > 0 else None
    )
    end_clock_line = _clock_end(scale)
    clock = clock_interfaces.Clock(main_clock_line, start_clock_line, end_clock_line)

    return clock


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
    from mutwo import diary_interfaces

    with diary_interfaces.open():
        clock_list = []
        for scale_position_tuple in [
            ((0, 0), (3, 0), (1, 0), (4, 0), (2, 0), (0, 0)),
            ((0, 0), (2, 0), (4, 0)),
            ((0, 0), (4, -1)),
            ((0, 0), (3, 0), (2, 0), (4, 0)),
        ]:
            clock = clock_list.append(make_clock(scale_position_tuple))

    clock_tuple = tuple(clock_list)
    project.render.notation(clock_tuple)
    project.render.midi(clock_tuple)
