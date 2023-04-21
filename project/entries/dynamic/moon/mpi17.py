import itertools

import ranges

from mutwo import common_generators
from mutwo import core_events
from mutwo import core_generators
from mutwo import core_parameters
from mutwo import music_events
from mutwo import project_generators
from mutwo import timeline_interfaces


# Similar to mpi15 and mpi14, but we use some global envelopes
# for not-random globally changing states.


ENVELOPE = core_generators.DynamicChoice(
    ["BASIC", "BASIC_QUIET", "BASIC_LOUD", "PLUCK_0", "PLUCK_1"],
    [
        core_events.Envelope([[0, 1], [1, 1]]),
        core_events.Envelope([[0, 1], [1, 1]]),
        core_events.Envelope([[0, 1], [1, 1]]),
        core_events.Envelope([[0, 1], [1, 1]]),
        core_events.Envelope([[0, 1], [1, 1]]),
    ],
)


FREQUENCY_FACTOR = core_generators.DynamicChoice(
    [2, 1, 0.5, 0.25, 0.125],
    [
        core_events.Envelope([[0, 1], [1, 1]]),
        core_events.Envelope([[0, 1], [1, 1]]),
        core_events.Envelope([[0, 1], [1, 1]]),
        core_events.Envelope([[0, 1], [1, 1]]),
        core_events.Envelope([[0, 1], [1, 1]]),
    ],
)


def is_supported(context, **kwargs):
    try:
        assert int(context.moon_phase_index) in (17,)
        assert hasattr(context.orchestration, "AEOLIAN_HARP")
    except AssertionError:
        return False
    return True


def main(context, random, **kwargs) -> timeline_interfaces.EventPlacement:
    scale = context.scale
    aeolian_harp = context.orchestration.AEOLIAN_HARP
    duration = context.end - context.start

    string_tuple, activity_level_tuple = find_main_chord(scale, aeolian_harp)
    string_and_activity_list = list(zip(string_tuple, activity_level_tuple))

    assert string_tuple

    for string in aeolian_harp.string_tuple:
        if string not in string_tuple:
            string_and_activity_list.append((string, ACTIVITY_LEVEL_TUPLE[-1]))

    assert len(string_and_activity_list) == aeolian_harp.TOTAL_STRING_COUNT

    sim = core_events.TaggedSimultaneousEvent(tag=aeolian_harp.name)

    string_and_activity_list.sort(
        key=lambda string_and_activity: string_and_activity[0].index
    )
    for string, activity in string_and_activity_list:
        sim.append(make_sequential_event(string, activity, duration, random))

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([sim]),
        context.start,
        context.end,
    )


def find_main_chord(scale, aeolian_harp):
    main_pitch = scale.scale_position_to_pitch((0, 0))
    main_pitch, *_ = aeolian_harp.get_pitch_variant_tuple(main_pitch)
    pitch_to_choose_from_tuple = tuple(
        s.tuning
        for s in aeolian_harp.string_tuple
        if s.tuning != main_pitch and s.tuning in scale.pitch_tuple
    )
    chord_tuple = project_generators.find_chord_tuple(
        (main_pitch,),
        pitch_to_choose_from_tuple,
        pitch_count_range=ranges.Range(3, 4),
        min_harmonicity=None,
        max_harmonicity=None,
    )
    chord = max(chord_tuple, key=lambda c: c.harmonicity)
    p0, p1 = (p for p in chord.pitch_tuple if p != main_pitch)
    h0, h1 = ((p - main_pitch).harmonicity_simplified_barlow for p in (p0, p1))
    if h0 > h1:
        level0, level1 = ACTIVITY_LEVEL_TUPLE[1], ACTIVITY_LEVEL_TUPLE[2]
    else:
        level1, level0 = ACTIVITY_LEVEL_TUPLE[1], ACTIVITY_LEVEL_TUPLE[2]
    string_tuple = chord_to_string_tuple(chord.pitch_tuple, aeolian_harp)
    activity_level_list = []

    # stupid pattern matching language design
    # https://stackoverflow.com/questions/67525257/capture-makes-remaining-patterns-unreachable
    class N(object):
        p_main = main_pitch
        p_0 = p0
        p_1 = p1

    for string in string_tuple:
        match string.tuning:
            case N.p_main:
                activity_level_list.append(ACTIVITY_LEVEL_TUPLE[0])
            case N.p_0:
                activity_level_list.append(level0)
            case N.p_1:
                activity_level_list.append(level1)
            case _:
                raise RuntimeError(str(string.tuning))
    return string_tuple, tuple(activity_level_list)


ACTIVITY_LEVEL_TUPLE = (9, 7, 6, 2)


def chord_to_string_tuple(chord, aeolian_harp):
    return tuple(s for s in aeolian_harp.string_tuple if s.tuning in chord)


def make_sequential_event(string, level, duration, random):
    activity_level = common_generators.ActivityLevel(
        next(LEVEL_TO_START_AT_CYCLE[level])
    )

    match level:
        case 2:
            tone_duration_range = ranges.Range(25, 40)
            rest_duration_range = ranges.Range(50, 105)
        case 6:
            tone_duration_range = ranges.Range(7, 11)
            rest_duration_range = ranges.Range(8, 15)
        case 7:
            tone_duration_range = ranges.Range(5, 15)
            rest_duration_range = ranges.Range(4, 10)
        case 9:
            tone_duration_range = ranges.Range(3, 5)
            rest_duration_range = ranges.Range(3, 7)
        case _:
            raise NotImplementedError(level)

    duration_range_tuple = (
        # rest
        rest_duration_range,
        # tone
        tone_duration_range,
    )

    sequential_event = core_events.SequentialEvent([])
    seq_duration = core_parameters.DirectDuration(0)

    while seq_duration < duration:
        pos = float(seq_duration / duration)
        note_like = music_events.NoteLike()
        if is_active := activity_level(level):
            note_like.pitch_list = [string.tuning]
            note_like.envelope = ENVELOPE.gamble_at(pos)
            note_like.frequency_factor = FREQUENCY_FACTOR.gamble_at(pos)

        duration_range = duration_range_tuple[is_active]
        note_like.duration = random.uniform(duration_range.start, duration_range.end)
        sequential_event.append(note_like)
        seq_duration += note_like.duration

    diff = seq_duration - duration
    sequential_event[-1].duration -= diff

    return sequential_event


LEVEL_TO_START_AT_CYCLE = {lv: itertools.cycle((0, 1, 2)) for lv in range(11)}
