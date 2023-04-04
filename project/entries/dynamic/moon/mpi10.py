import ranges

from mutwo import common_generators
from mutwo import core_events
from mutwo import music_events
from mutwo import project_generators
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert int(context.moon_phase_index) in (10, 11, 12)
        assert hasattr(context.orchestration, "AEOLIAN_HARP")
    except AssertionError:
        return False
    return True


def main(context, random, **kwargs) -> timeline_interfaces.EventPlacement:
    scale = context.scale
    aeolian_harp = context.orchestration.AEOLIAN_HARP
    duration = context.end - context.start

    main_chord = find_main_chord(scale, aeolian_harp)
    side_chord = find_side_chord(scale, aeolian_harp, main_chord)

    chord_tuple = (side_chord, main_chord)

    sim = core_events.TaggedSimultaneousEvent(
        [
            core_events.SequentialEvent([core_events.SimpleEvent(duration)])
            for _ in range(9)
        ],
        tag=aeolian_harp.name,
    )

    # We use local activity level :)
    activity_level = common_generators.ActivityLevel()

    # True for main chord,
    # False for low chord
    chord_activity_distribution = 7

    # True for tone
    # False for rest
    tone_rest_activity_level = 6

    absolute_time = 0

    duration_range_tuple = (
        # rest
        ranges.Range(65, 200),
        # tone
        ranges.Range(11, 17),
    )

    while absolute_time < duration:
        is_tone = activity_level(tone_rest_activity_level)
        duration_range = duration_range_tuple[is_tone]
        min_duration, max_duration = duration_range.start, duration_range.end
        d = random.uniform(min_duration, max_duration)
        new_absolute_time = absolute_time + d
        if new_absolute_time > duration:
            new_absolute_time = duration
            d = new_absolute_time - absolute_time
        if is_tone and d > min_duration:
            chord = chord_tuple[activity_level(chord_activity_distribution)]
            for string in chord:
                n = music_events.NoteLike(string.tuning, d)
                n.envelope = random.choice(["BASIC_QUIET", "PLUCK_0", "PLUCK_1"])
                n.frequency_factor = 0.5
                sim[string.index].squash_in(absolute_time, n)
        absolute_time = new_absolute_time
        print(absolute_time)

    print("FINISHED ENTRY")

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
    return chord_to_string_tuple(chord.pitch_tuple, aeolian_harp)


def find_side_chord(scale, aeolian_harp, main_chord):
    pitch_to_choose_from_tuple = tuple(
        s.tuning for s in aeolian_harp.string_tuple if s.tuning not in main_chord
    )
    chord_tuple = project_generators.find_chord_tuple(
        tuple([]),
        pitch_to_choose_from_tuple,
        pitch_count_range=ranges.Range(2, 3),
        min_harmonicity=None,
        max_harmonicity=None,
    )
    chord = max(chord_tuple, key=lambda c: c.harmonicity)
    return chord_to_string_tuple(chord.pitch_tuple, aeolian_harp)


def chord_to_string_tuple(chord, aeolian_harp):
    return tuple(s for s in aeolian_harp.string_tuple if s.tuning in chord)
