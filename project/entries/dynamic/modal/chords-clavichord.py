import bisect
import itertools
import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_converters
from mutwo import project_generators
from mutwo import project_parameters
from mutwo import timeline_interfaces


def is_supported(context, pitch=None, **kwargs):
    try:
        assert isinstance(context.modal_event, clock_events.ModalEvent1)
        orchestration = context.orchestration
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert isinstance(instrument, project_parameters.Clavichord)
    except AssertionError:
        return False
    return True


def main(
    context,
    random,
    activity_level,
    event_count_to_average_tone_duration={
        1: 13,
        2: 11,
        3: 9.8,
        4: 8.8,
        5: 7.5,
        6: 6.75,
        7: 5,
    },
    **kwargs,
) -> timeline_interfaces.EventPlacement:
    orchestration = context.orchestration
    instrument = orchestration[0]
    modal_event = context.modal_event
    scale = modal_event.scale
    pitch = modal_event.pitch

    sequential_event = make_sequential_event(
        instrument, scale, pitch, random, activity_level
    )
    simultaneous_event = core_events.SimultaneousEvent(
        [
            core_events.TaggedSimultaneousEvent(
                [sequential_event],
                tag=instrument.name,
            )
        ]
    )

    start_range, end_range = make_range_pair(
        len(sequential_event), event_count_to_average_tone_duration, modal_event
    )

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


def make_range_pair(
    event_count, event_count_to_average_tone_duration, modal_event_to_convert
):
    duration_in_seconds = modal_event_to_convert.clock_event.metrize(
        mutate=False
    ).duration.duration_in_floats

    try:
        average_tone_duration_in_seconds = event_count_to_average_tone_duration[
            event_count
        ]
    except KeyError:
        average_tone_duration_in_seconds = 10
    duration = modal_event_to_convert.clock_event.duration

    return project_converters.AverageNoteDurationToRangePair().convert(
        average_tone_duration_in_seconds, event_count, duration_in_seconds, duration
    )


def make_sequential_event(instrument, scale, pitch, random, activity_level):
    scale_degree = scale.pitch_to_scale_degree(pitch)

    if scale_degree == 0:
        chord_count_pick_tuple = (1, 2, 3, 4, 5)
    else:
        chord_count_pick_tuple = (1, 2, 3)

    chord_count = random.choice(chord_count_pick_tuple)
    side_pitch_direction = (-1, 1)[activity_level(5)]
    octave_delta = random.choice([1, 1, 1, 2]) * side_pitch_direction
    main_pitch_octave_scale_position = random.choice([0, -1, 1])
    add_fill_up_pitch_tuple_tuple = tuple(
        random.choice([(True, True), (False, True), (True, False), (False, False)])
        for _ in range(chord_count)
    )

    pitch_tuple = instrument.pitch_tuple

    is_chord_harmonic_tuple = make_is_chord_harmonic_tuple(chord_count)
    main_pitch_tuple = make_main_pitch_tuple(
        scale_degree,
        scale,
        chord_count,
        main_pitch_octave_scale_position,
        octave_delta,
        pitch_tuple,
        activity_level,
    )
    side_pitch_tuple = make_side_pitch_tuple(
        scale,
        pitch_tuple,
        main_pitch_tuple,
        main_pitch_octave_scale_position,
        octave_delta,
        chord_count,
        activity_level,
    )
    fill_in_pitches = find_fill_in_pitches(
        main_pitch_tuple, side_pitch_tuple, pitch_tuple, add_fill_up_pitch_tuple_tuple
    )

    chord_tuple = make_chord_tuple(
        pitch_tuple,
        is_chord_harmonic_tuple,
        main_pitch_tuple,
        side_pitch_tuple,
        instrument,
        random,
        fill_in_pitches,
    )

    sequential_event = core_events.SequentialEvent([])
    for pitch_tuple in chord_tuple:
        n = music_events.NoteLike(
            pitch_tuple, duration=random.choice([1, 0.75, 1.5, 2]), volume="p"
        )
        sequential_event.append(n)
    return sequential_event


def make_main_pitch_tuple(
    scale_degree,
    scale,
    chord_count,
    main_pitch_octave_scale_position,
    octave_delta,
    pitch_tuple,
    activity_level,
) -> tuple[music_parameters.JustIntonationPitch, ...]:
    scale_degree_count = len(set(scale.scale_degree_tuple))
    assert scale_degree_count == 5
    if scale_degree == 0:
        main_pitch_cycle = itertools.cycle((0,))
    else:
        low, high = ((scale_degree + n) % scale_degree_count for n in (-1, 1))
        if activity_level(4):
            pattern = (scale_degree, low, scale_degree, high)
        else:
            pattern = (scale_degree, high, scale_degree, low)
        main_pitch_cycle = itertools.cycle(pattern)

    main_pitch_list = []
    for _ in range(chord_count):
        p = scale.scale_position_to_pitch(
            (next(main_pitch_cycle), main_pitch_octave_scale_position)
        )
        main_pitch_list.append(p)

    if chord_count > 2:
        add_variation(main_pitch_list, octave_delta, pitch_tuple, -1, 1)

    return tuple(reversed(main_pitch_list))


def make_side_pitch_tuple(
    scale,
    pitch_tuple,
    main_pitch_tuple,
    main_pitch_octave_scale_position,
    octave_delta,
    chord_count,
    activity_level,
):
    assert octave_delta != 0
    side_pitch_octave_scale_position = main_pitch_octave_scale_position + octave_delta
    filtered_pitch_list = []
    for i in range(5):
        try:
            p = scale.scale_position_to_pitch((i, side_pitch_octave_scale_position))
        except ValueError:
            continue
        filtered_pitch_list.append(p)
    # Need to be playable by instrument, therefore additional filter
    if not (
        filtered_pitch_tuple := tuple(
            p for p in filtered_pitch_list if p in pitch_tuple
        )
    ):
        return tuple(None for _ in main_pitch_tuple)
    c = find_champion(main_pitch_tuple[-1], filtered_pitch_tuple)
    side_pitch_list = list(
        reversed([c if i % 2 == 0 else None for i, _ in enumerate(main_pitch_tuple)])
    )

    def direction_to_index_tuple(index, direction):
        if direction:
            return index + 1, index + 4
        else:
            return index - 3, index

    for i, m0, m1, s0, s1 in zip(
        range(chord_count),
        main_pitch_tuple,
        main_pitch_tuple[1:],
        side_pitch_list,
        side_pitch_list[1:],
    ):
        if s0 is None:
            direction = m1 > m0
            # Sometimes switch normal direction for some
            # variation.
            if activity_level(2):
                direction = not direction
            s1_index = pitch_tuple.index(s1)
            index_tuple = direction_to_index_tuple(s1_index, direction)
            candidate_tuple = pitch_tuple[index_tuple[0] : index_tuple[1]]
            if not candidate_tuple:
                index_tuple = direction_to_index_tuple(s1_index, not direction)
                candidate_tuple = pitch_tuple[index_tuple[0] : index_tuple[1]]
            if not candidate_tuple:
                candidate_tuple = (pitch_tuple[s1_index],)
            side_pitch_list[i] = find_champion(m0, candidate_tuple)

    for p in side_pitch_list:
        assert p

    if activity_level(3):
        add_variation(side_pitch_list, octave_delta, pitch_tuple, 1, -1)

    return tuple(side_pitch_list)


def find_champion(
    partner,
    candidate_tuple,
    prohibited_interval_tuple=(music_parameters.JustIntonationPitch("1/1"),),
):
    assert candidate_tuple
    c, f = None, 0
    for p in candidate_tuple:
        interval = p - partner
        if interval.normalize(mutate=False) in prohibited_interval_tuple:
            continue
        if (local_f := interval.harmonicity_simplified_barlow) > f or c is None:
            c, f = p, local_f
    # This means all of our pitches were inside the prohibited_interval_tuple.
    # Let's try it again and be less strict.
    if c is None:
        return find_champion(partner, candidate_tuple, tuple([]))
    return c


def find_fill_in_pitches(
    main_pitch_tuple, side_pitch_tuple, pitch_tuple, add_fill_up_pitch_tuple_tuple
):
    pitch_count = len(pitch_tuple)

    def r2indexr(r):
        indexr = []
        for p in r:
            i0 = bisect.bisect_left(pitch_tuple, p)
            if pitch_count > i0 + 1:
                i1 = i0 + 1
                p0, p1 = pitch_tuple[i0], pitch_tuple[i1]
                if abs(p0.get_pitch_interval(p).interval) > abs(
                    p1.get_pitch_interval(p).interval
                ):
                    i = i1
                else:
                    i = i0
            else:
                i = i0
            indexr.append(i)
        return indexr

    max_interval = music_parameters.JustIntonationPitch("3/2")

    fill_up_pitch_list = []
    for main_pitch, side_pitch, add_fill_up_pitch_tuple in zip(
        main_pitch_tuple, side_pitch_tuple, add_fill_up_pitch_tuple_tuple
    ):
        if not main_pitch or not side_pitch:
            fill_up_pitch_list.append(tuple([]))
            continue

        add_fill_up_main, add_fill_up_side = add_fill_up_pitch_tuple

        if main_pitch > side_pitch:
            r0 = (side_pitch, side_pitch + max_interval)
            r0_valid = add_fill_up_side
            r1 = (main_pitch - max_interval, main_pitch)
            r1_valid = add_fill_up_main
        else:
            r0 = (main_pitch, main_pitch + max_interval)
            r0_valid = add_fill_up_main
            r1 = (side_pitch - max_interval, side_pitch)
            r1_valid = add_fill_up_side

        r0, r1 = (r2indexr(r) for r in (r0, r1))
        if r0_valid and r1_valid and r0[1] > r1[0]:
            r0[1] = r1[0]

        if r1[0] < r0[0]:
            r1[0] = r0[0]
        if r0[1] > r1[1]:
            r0[1] = r0[1]

        pitch_to_choose_tuple_list = [
            tuple(pitch_tuple[i] for i in range(*r))
            for r, is_valid in ((r0, r0_valid), (r1, r1_valid))
            if is_valid
        ]

        pitch_to_choose_tuple_list = [t for t in pitch_to_choose_tuple_list if t]

        fill_up_pitch_list.append(
            find_champion2((main_pitch, side_pitch), pitch_to_choose_tuple_list)
        )

    return tuple(fill_up_pitch_list)


def find_champion2(
    predefined_pitch_list,
    candidate_pitch_tuple_tuple,
):
    if not candidate_pitch_tuple_tuple:
        return tuple()
    c, f = None, 0
    for ptuple in itertools.product(*candidate_pitch_tuple_tuple):
        if any([predefinedp in ptuple for predefinedp in predefined_pitch_list]):
            continue
        f_local = sum(
            [
                (p0 - p1).harmonicity_simplified_barlow
                for p0, p1 in itertools.combinations(predefined_pitch_list + ptuple, 2)
            ]
        )
        if c is None or f_local > f:
            f = f_local
            c = ptuple
    if c is None:
        return tuple([])
    return c


def add_variation(pitch_list, octave_delta, pitch_tuple, direction0, direction1):
    if octave_delta > 0:
        octave_delta_direction = direction0
    else:
        octave_delta_direction = direction1
    variation = pitch_list[0].register(
        pitch_list[0].octave + octave_delta_direction, mutate=False
    )
    if variation in pitch_tuple:
        pitch_list[0] = variation


def make_chord_tuple(
    pitch_tuple,
    is_chord_harmonic_tuple,
    main_pitch_tuple,
    side_pitch_tuple,
    instrument,
    random,
    fill_in_pitches,
):
    return tuple(
        (m, s) + p if s else (m,) + p
        for m, s, p in zip(main_pitch_tuple, side_pitch_tuple, fill_in_pitches)
    )


def make_is_chord_harmonic_tuple(chord_count):
    is_chord_harmonic_cycle = itertools.cycle((True, False))
    return tuple(
        reversed(tuple(next(is_chord_harmonic_cycle) for _ in range(chord_count)))
    )
