from quicktions import Fraction as f

import numpy as np
import ranges

from mutwo import core_converters
from mutwo import clock_converters
from mutwo import clock_events
from mutwo import clock_interfaces
from mutwo import common_generators
from mutwo import core_events
from mutwo import diary_converters
from mutwo import project_converters
from mutwo import timeline_interfaces

import project


def make_clock(poem_index, poem_line, before_rest_duration=0) -> clock_interfaces.Clock:
    print("make clock for", poem_line, "...")

    scale = project.constants.PENTATONIC_SCALE_TUPLE[poem_index]

    match poem_index % 4:
        case 0:
            part_count = 2
            energy = 61
        case 1:
            part_count = 3
            energy = 51
        case 2:
            part_count = 2
            energy = 41
        case 3:
            part_count = 1
            energy = 51

    if not poem_line:
        scale_position_tuple = tuple((0, 0) for _ in range(part_count * 4))
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
            clock_events.ModalEvent0(start_pitch, end_pitch, scale, energy=energy)
            for start_pitch, end_pitch in zip(root_pitch_tuple, root_pitch_tuple[1:])
        ]
    )

    project.clocks.apply_clock_events(modal_sequential_event)

    if part_count >= 3:
        insert_modal_event(
            modal_sequential_event,
            scale,
            energy=-4,
            index=7,
            duration=f(8, 16),
        )

    if part_count >= 2:
        if part_count >= 3:
            energy = -3
        else:
            energy = -4
        insert_modal_event(
            modal_sequential_event,
            scale,
            energy=energy,
            index=3,
            duration=f(8, 16),
        )

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
                add_mod1=True,
            ),
            diary_converters.Modal0SequentialEventToEventPlacementTuple(
                orchestration=project.constants.ORCHESTRATION.get_subset("V"),
                add_mod1=True,
            ),
            diary_converters.Modal0SequentialEventToEventPlacementTuple(
                orchestration=project.constants.ORCHESTRATION.get_subset("V", "HARP"),
                add_mod1=False,
            ),
            diary_converters.Modal0SequentialEventToEventPlacementTuple(
                orchestration=project.constants.ORCHESTRATION.get_subset(
                    "GLOCKENSPIEL",
                    "V",
                    "HARP",
                ),
                add_mod1=False,
            ),
        )
    ).convert(modal_sequential_event)

    # Fix overlaps
    main_clock_line.resolve_conflicts(
        [
            TuningForkHitStrategy(),
            TagCountStrategy(),
            timeline_interfaces.AlternatingStrategy(),
        ],
        is_conflict=is_conflict,
    )

    start_clock_line = (
        _clock_rest(before_rest_duration) if before_rest_duration > 0 else None
    )
    end_clock_line = _clock_end(scale)
    clock = clock_interfaces.Clock(main_clock_line, start_clock_line, end_clock_line)

    return clock


def is_conflict(event_placement_0, event_placement_1):
    tag_tuple0, tag_tuple1 = (
        ep.tag_tuple for ep in (event_placement_0, event_placement_1)
    )

    # Avoid overlaps between bowed tuning forks and other percussion
    # sounds (because the player need to hold the tuning fork with one
    # hand).
    if may_be_bowed_tuning_fork_conflict(event_placement_0, event_placement_1):
        for n in get_overlapping_tuning_fork_note_tuple(
            event_placement_0, event_placement_1
        ):
            if (
                hasattr(n, "notation_indicator_collection")
                and n.notation_indicator_collection.duration_line.is_active
            ):
                return True

    # Standard logic
    share_instruments = bool(set(tag_tuple0).intersection(set(tag_tuple1)))
    return share_instruments


def may_be_bowed_tuning_fork_conflict(event_placement_0, event_placement_1):
    tag_tuple0, tag_tuple1 = (
        ep.tag_tuple for ep in (event_placement_0, event_placement_1)
    )
    return (
        project.constants.ORCHESTRATION.PCLOCK.name in tag_tuple0
        and project.constants.ORCHESTRATION.GLOCKENSPIEL.name in tag_tuple1
    ) or (
        project.constants.ORCHESTRATION.PCLOCK.name in tag_tuple1
        and project.constants.ORCHESTRATION.GLOCKENSPIEL.name in tag_tuple0
    )


def get_overlapping_tuning_fork_note_tuple(event_placement_0, event_placement_1):
    glockenspiel_event, glockenspiel_ep = get_glockenspiel_event(
        event_placement_0, event_placement_1
    )
    adjusted_glockenspiel_event = glockenspiel_event.set(
        "duration", glockenspiel_ep.duration, mutate=False
    )
    _, pclock_ep = get_pclock_event(event_placement_0, event_placement_1)
    pclock_duration_range = pclock_ep.time_range
    overlapping_tuning_fork_note_list = []
    for sequential_event_copy, sequential_event in zip(
        # We need the duration information from the copied event
        # (because we only copied the event in order to scale to real
        # duration), but want to have the original note (because this
        # is the one which needs to be adjusted).
        adjusted_glockenspiel_event,
        glockenspiel_event,
    ):
        (
            absolute_time_tuple,
            duration,
        ) = sequential_event_copy._absolute_time_tuple_and_duration
        for start, end, n in zip(
            absolute_time_tuple, absolute_time_tuple[1:] + (duration,), sequential_event
        ):
            r_start = start + glockenspiel_ep.min_start
            r_end = end + glockenspiel_ep.min_start
            if r_start in pclock_duration_range or r_end in pclock_duration_range:
                overlapping_tuning_fork_note_list.append(n)
    return tuple(overlapping_tuning_fork_note_list)


def get_glockenspiel_event(event_placement_0, event_placement_1):
    return get_tag_event(
        event_placement_0,
        event_placement_1,
        project.constants.ORCHESTRATION.GLOCKENSPIEL.name,
    )


def get_pclock_event(event_placement_0, event_placement_1):
    return get_tag_event(
        event_placement_0,
        event_placement_1,
        project.constants.ORCHESTRATION.PCLOCK.name,
    )


def get_tag_event(event_placement_0, event_placement_1, tag):
    tag_tuple0, tag_tuple1 = (
        ep.tag_tuple for ep in (event_placement_0, event_placement_1)
    )
    if tag in tag_tuple0:
        ep = event_placement_0
    else:
        ep = event_placement_1
    return ep.event[tag], ep


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


class TuningForkHitStrategy(timeline_interfaces.ConflictResolutionStrategy):
    def __init__(self, fix_level: int = 5):
        # fix_level = 10    => always fix
        # fix_level = 0     => never fix
        self.fix_level = fix_level
        self.activity_level = common_generators.ActivityLevel()
        self.split_activity_level = common_generators.ActivityLevel(1)

    def resolve_conflict(self, timeline, conflict) -> bool:
        event_placement_0, event_placement_1 = conflict.left, conflict.right
        if may_be_bowed_tuning_fork_conflict(event_placement_0, event_placement_1):
            # Don't fix always, because this would be a bit boring :)
            if self.activity_level(self.fix_level):
                self._solve(event_placement_0, event_placement_1)
                return True
        return False

    def _solve(self, event_placement_0, event_placement_1):
        for n in get_overlapping_tuning_fork_note_tuple(
            event_placement_0, event_placement_1
        ):
            try:
                n.notation_indicator_collection.duration_line.is_active = False
            except AttributeError:
                pass

        # Sometimes split some of the glockenspiel notes, which needed to
        # be separated.
        glockenspiel_event, _ = get_glockenspiel_event(
            event_placement_0, event_placement_1
        )
        glockenspiel_event = glockenspiel_event[0]  # seq event
        for absolute_time, n in zip(
            glockenspiel_event.absolute_time_tuple, glockenspiel_event
        ):
            split = False
            try:
                split = (
                    n.notation_indicator_collection.duration_line.is_active == False
                    and n.pitch_list
                )
            except AttributeError:
                pass
            if split and self.split_activity_level(5):
                glockenspiel_event.split_child_at(
                    absolute_time + (n.duration.duration * f(1, 2))
                )


class TagCountStrategy(timeline_interfaces.TagCountStrategy):
    def __init__(self, prefer_more_level: int = 8):
        self.prefer_more_level = prefer_more_level
        self.activity_level = common_generators.ActivityLevel()
        self.tag_count_more = timeline_interfaces.TagCountStrategy()
        self.tag_count_fewer = timeline_interfaces.TagCountStrategy(False)

    def resolve_conflict(self, timeline, conflict) -> bool:
        if self.activity_level(self.prefer_more_level):
            return self.tag_count_more.resolve_conflict(timeline, conflict)
        else:
            return self.tag_count_fewer.resolve_conflict(timeline, conflict)


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
