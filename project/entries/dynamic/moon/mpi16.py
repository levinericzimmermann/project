from mutwo import common_generators
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities
from mutwo import music_converters
from mutwo import music_events
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert int(context.moon_phase_index) in (16,)
        assert hasattr(context.orchestration, "AEOLIAN_HARP")
    except AssertionError:
        return False
    return True


# Idea
#
# - almost all strings can sound equally often
# - we use a rhythm, so there is a common set of beats/bars
#   and strings are only allowed to place a new changing event
#   on a new bar => at some points it's more likely that a new
#   event happens than on another point
# - we use a rhythm with 9 beats. Each string has its own beat
#   and is only allowed to place a new event on its own beat.
# - Different beats have different likelihoods for new events.
#   The most harmonic pitch (main pitch) has the highest likelihood,
#   all other strings follow according to harmonicity to main pitch.
# - There is also the likelihood for tone vs. rest: the more harmonic
#   a pitch is there more likely it is to place a tone.
# - Each rhythmic cycle lasts around 11 seconds, so the shortest possible
#   event lasts 11 seconds.


def main(context, random, **kwargs) -> timeline_interfaces.EventPlacement:
    scale = context.scale
    aeolian_harp = context.orchestration.AEOLIAN_HARP
    duration = context.end - context.start

    print([scale.scale_position_to_pitch((n, 0)) for n in range(5)])
    1/0

    main_pitch = scale.scale_position_to_pitch((0, 0))
    string_and_harmonicity = []
    for string in aeolian_harp.string_tuple:
        harmonicity = (main_pitch - string.tuning).harmonicity_simplified_barlow
        string_and_harmonicity.append((string, harmonicity))

    indispensability = music_converters.RhythmicalStrataToIndispensability().convert(
        (3, 3)
    )
    indispensability_sorted = sorted(indispensability, reverse=True)

    beat_count = aeolian_harp.TOTAL_STRING_COUNT
    assert beat_count == 9

    metronome = core_events.SequentialEvent([])
    metronome_duration = core_parameters.DirectDuration(0)
    while metronome_duration < duration:
        m = core_events.SequentialEvent(
            [core_events.SimpleEvent(1) for _ in range(beat_count)]
        )
        t = core_parameters.DirectTempoPoint(random.uniform(40, 50))
        m.tempo_envelope = core_events.TempoEnvelope([[0, t], [beat_count, t]])
        m.metrize()
        metronome.extend(m)
        metronome_duration += m.duration

    metronome.duration = duration
    metronome_absolute_time_tuple = metronome.absolute_time_tuple

    mi_i, max_i = min(indispensability), max(indispensability)
    event_likelihood_tuple = tuple(
        core_utilities.scale(v, mi_i, max_i, 0.1, 1) for v in indispensability
    )

    string_data_list = []
    for string_role_index, string_and_harmonicity in enumerate(
        sorted(string_and_harmonicity, key=lambda sah: sah[1], reverse=True)
    ):
        beat_index = indispensability.index(indispensability_sorted[string_role_index])
        tone_likelihood = 10 - string_role_index
        string_data_list.append(
            (string_and_harmonicity[0], beat_index, tone_likelihood)
        )

    assert string_data_list
    assert len(string_data_list) == aeolian_harp.TOTAL_STRING_COUNT

    sim = core_events.TaggedSimultaneousEvent(tag=aeolian_harp.name)

    for string, beat_index, tone_likelihood in string_data_list:
        sim.append(
            make_sequential_event(
                string,
                beat_index,
                tone_likelihood,
                event_likelihood_tuple,
                random,
                metronome,
                metronome_absolute_time_tuple,
                duration,
                beat_count,
            )
        )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([sim]),
        context.start,
        context.end,
    )


def make_sequential_event(
    string,
    beat_index,
    tone_likelihood,
    event_likelihood_tuple,
    random,
    metronome,
    metronome_absolute_time_tuple,
    duration,
    beat_count,
):
    activity_level = common_generators.ActivityLevel()

    sequential_event = core_events.SequentialEvent([])

    index_tuple = range(beat_index, len(metronome), beat_count)
    for i0, i1 in zip(index_tuple, index_tuple[1:]):
        t0, t1 = (metronome_absolute_time_tuple[i] for i in (i0, i1))

        if t0 != 0 and not sequential_event:
            sequential_event.append(core_events.SimpleEvent(t0))

        e_duration = t1 - t0

        # No new event
        if random.random() > event_likelihood_tuple[beat_index]:
            sequential_event[-1].duration += e_duration
            continue

        note_like = music_events.NoteLike(duration=e_duration)
        if activity_level(tone_likelihood):
            note_like.pitch_list = [string.tuning]
            note_like.envelope = random.choice(
                ["BASIC", "BASIC_QUIET", "BASIC_LOUD", "PLUCK_0", "PLUCK_1"]
            )
            note_like.frequency_factor = random.choice([1, 0.5, 0.25, 0.125, 2])
        sequential_event.append(note_like)

    diff = duration - sequential_event.duration
    if diff > 0:
        sequential_event.append(core_events.SimpleEvent(diff))
    elif diff < 0:
        raise RuntimeError()

    assert len(sequential_event) > 2

    return sequential_event
