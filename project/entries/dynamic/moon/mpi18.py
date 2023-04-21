import ranges

from mutwo import core_events
from mutwo import music_events
from mutwo import project_generators
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert int(context.moon_phase_index) in (18,)
        assert hasattr(context.orchestration, "AEOLIAN_HARP")
    except AssertionError:
        return False
    return True


def main(context, random, **kwargs) -> timeline_interfaces.EventPlacement:
    scale = context.scale
    aeolian_harp = context.orchestration.AEOLIAN_HARP
    duration = context.end - context.start

    string_tuple = find_main_chord(scale, aeolian_harp)

    assert string_tuple

    sim = core_events.TaggedSimultaneousEvent(
        tag=aeolian_harp.name,
    )
    for string in aeolian_harp.string_tuple:
        n = music_events.NoteLike(duration=duration)
        if string in string_tuple:
            n.pitch_list = [string.tuning]
            n.envelope = "BASIC_QUIET"
            n.frequency_factor = 0.5
        sim.append(core_events.SequentialEvent([n]))

    assert len(sim) == aeolian_harp.TOTAL_STRING_COUNT

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

    string_tuple = chord_to_string_tuple(chord.pitch_tuple, aeolian_harp)

    return string_tuple


def chord_to_string_tuple(chord, aeolian_harp):
    return tuple(s for s in aeolian_harp.string_tuple if s.tuning in chord)
