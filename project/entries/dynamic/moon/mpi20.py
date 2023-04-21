import itertools
import yamm

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


def is_supported(context, **kwargs):
    try:
        assert int(context.moon_phase_index) in (20,)
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

    envelope, frequency_factor, silence = make_dynamic_choice_tuple(duration, random)

    sim = core_events.TaggedSimultaneousEvent(tag=aeolian_harp.name)

    string_and_activity_list.sort(
        key=lambda string_and_activity: string_and_activity[0].index
    )
    for string, activity in string_and_activity_list:
        print(string, activity)
        sim.append(
            make_sequential_event(
                string, activity, duration, random, envelope, frequency_factor, silence
            )
        )

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


def make_sequential_event(string, level, duration, random, envelope, frequency_factor, silence):
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
        if silence.gamble_at(pos) and (is_active := activity_level(level)):
            note_like.pitch_list = [string.tuning]
            note_like.envelope = envelope.gamble_at(pos)
            note_like.frequency_factor = frequency_factor.gamble_at(pos)

        duration_range = duration_range_tuple[is_active]
        note_like.duration = random.uniform(duration_range.start, duration_range.end)
        sequential_event.append(note_like)
        seq_duration += note_like.duration

    diff = seq_duration - duration
    sequential_event[-1].duration -= diff

    return sequential_event


LEVEL_TO_START_AT_CYCLE = {lv: itertools.cycle((0, 1, 2)) for lv in range(11)}


class State(object):
    _default_envelope_state = dict(
        BASIC=0, BASIC_QUIET=0, BASIC_LOUD=0, PLUCK_0=0, PLUCK_1=0
    )
    _frequency_factor_state = {2: 0, 1: 0, 0.5: 0, 0.25: 0, 0.125: 0}
    _default_silence_state = {True: 1, False: 0}

    def __init__(
        self,
        envelope_state: dict[str, float] = {},
        frequency_state: dict[float, float] = {},
        silence_state: dict[bool, float] = {},
    ):
        for k, v in self._default_envelope_state.items():
            envelope_state.setdefault(k, v)

        for k, v in self._frequency_factor_state.items():
            frequency_state.setdefault(k, v)

        for k, v in self._default_silence_state.items():
            silence_state.setdefault(k, v)

        self.envelope_state = envelope_state
        self.frequency_state = frequency_state
        self.silence_state = silence_state


STATE_DICT = dict(
    stable=State(dict(BASIC=1, BASIC_QUIET=1), {1: 1, 0.5: 0.85, 2: 0.25}),
    pluck=State(dict(PLUCK_0=1, PLUCK_1=1), {1: 1, 0.5: 0.85, 2: 0.25}),
    overtones=State(dict(BASIC_QUIET=1, PLUCK_0=1), {0.125: 1, 0.25: 0.25}),
    silence=State({}, {}, {True: 0, False: 1}),
)

STATE_DURATION_RANGE = dict(
    stable=ranges.Range(60 * 1, 60 * 4),
    pluck=ranges.Range(60 * 2, 60 * 4),
    overtones=ranges.Range(60 * 2, 60 * 3),
    silence=ranges.Range(20, 60),
)

STATE_MARKOV_CHAIN = yamm.chain.Chain(
    {
        ("stable",): dict(silence=50, pluck=30, overtones=30),
        ("silence",): dict(stable=10, pluck=10, overtones=10),
        ("pluck",): dict(silence=40, pluck=20, overtones=20, stable=20),
        ("overtones",): dict(silence=40, pluck=20, stable=20),
    }
)
STATE_MARKOV_CHAIN.make_deterministic_map()


def make_dynamic_choice_tuple(duration, random):
    envelope_envelope_data = dict(
        BASIC=[], BASIC_QUIET=[], BASIC_LOUD=[], PLUCK_0=[], PLUCK_1=[]
    )
    frequency_factor_envelope_data = {2: [], 1: [], 0.5: [], 0.25: [], 0.125: []}
    silence_envelope_data = {True: [], False: []}
    env_data_tuple = (
        envelope_envelope_data,
        frequency_factor_envelope_data,
        silence_envelope_data,
    )

    state_gen = STATE_MARKOV_CHAIN.walk_deterministic(("stable",))
    d = 0
    while d < duration:
        state_name = next(state_gen)
        drange = STATE_DURATION_RANGE[state_name]
        local_duration = random.uniform(drange.start, drange.end)
        state = STATE_DICT[state_name]

        for state_data, env_data in zip(
            (state.envelope_state, state.frequency_state, state.silence_state),
            env_data_tuple,
        ):
            for k, v in state_data.items():
                env_data[k].append((d, v))

        d += local_duration

    dynamic_choice_list = []

    for env_data in env_data_tuple:
        items, envs = [], []
        for k, v in env_data.items():
            items.append(k)
            envs.append(core_events.Envelope(v).set('duration', 1))
        for e in envs:
            assert e.duration == 1
            break
        dynamic_choice_list.append(core_generators.DynamicChoice(items, envs))

    assert len(dynamic_choice_list) == 3
    return tuple(dynamic_choice_list)
