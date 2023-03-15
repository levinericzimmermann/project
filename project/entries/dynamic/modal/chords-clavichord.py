import itertools
import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
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
    context, random, activity_level, **kwargs
) -> timeline_interfaces.EventPlacement:
    orchestration = context.orchestration
    instrument = orchestration[0]
    scale = context.modal_event.scale
    pitch = context.modal_event.pitch

    sequential_event = make_sequential_event(instrument, scale, pitch, random)
    simultaneous_event = core_events.SimultaneousEvent(
        [
            core_events.TaggedSimultaneousEvent(
                [sequential_event],
                tag=instrument.name,
            )
        ]
    )

    duration = context.modal_event.clock_event.duration
    start_range = ranges.Range(duration * 0.3, duration * 0.35)
    end_range = ranges.Range(duration * 0.65, duration * 0.7)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


def make_sequential_event(instrument, scale, pitch, random):
    chord_count = random.choice([1, 2, 3, 4])

    scale_degree = scale.pitch_to_scale_degree(pitch)
    is_chord_harmonic_tuple = make_is_chord_harmonic_tuple(chord_count)
    chord_ambitus_tuple = make_chord_ambitus_tuple(chord_count, random)
    pitch_count_tuple = make_pitch_count_tuple(chord_count, random)
    main_pitch_tuple = make_main_pitch_tuple(
        scale_degree, scale, chord_count, chord_ambitus_tuple, random
    )
    pitch_tuple = instrument.pitch_tuple

    chord_tuple = make_chord_tuple(
        pitch_tuple,
        is_chord_harmonic_tuple,
        main_pitch_tuple,
        pitch_count_tuple,
        chord_ambitus_tuple,
        random,
    )

    sequential_event = core_events.SequentialEvent([])
    for pitch_tuple in chord_tuple:
        n = music_events.NoteLike(
            pitch_tuple, duration=random.choice([1, 0.75, 1.5, 2]), volume="p"
        )
        sequential_event.append(n)
    return sequential_event


def make_chord_tuple(
    pitch_tuple,
    is_chord_harmonic_tuple,
    main_pitch_tuple,
    pitch_count_tuple,
    chord_ambitus_tuple,
    random,
):
    chord_list = []
    for is_chord_harmonic, main_pitch, pitch_count, ambitus in zip(
        is_chord_harmonic_tuple,
        main_pitch_tuple,
        pitch_count_tuple,
        chord_ambitus_tuple,
    ):
        if is_chord_harmonic:
            min_interval = music_parameters.JustIntonationPitch("7/6")
            min_harmonicity = music_parameters.JustIntonationPitch(
                "3/2"
            ).harmonicity_simplified_barlow
            max_harmonicity = None
        else:
            min_interval = music_parameters.JustIntonationPitch("10/9")
            min_harmonicity = music_parameters.JustIntonationPitch(
                "5/4"
            ).harmonicity_simplified_barlow
            max_harmonicity = None

        chord_tuple = project_generators.find_chord_tuple(
            (main_pitch,),
            pitch_tuple,
            ranges.Range(pitch_count, pitch_count + 1),
            min_harmonicity,
            max_harmonicity,
            ambitus,
            min_interval,
        )
        if chord_list:
            chord_difference_tuple = project_generators.make_chord_difference_tuple(
                (chord_list[-1],), chord_tuple
            )
            chord_tuple = tuple(
                cdelta.chord1 for cdelta in chord_difference_tuple if len(cdelta.only1) >= len(cdelta.intersection)
            )
        if chord_tuple:
            chord_list.append(chord_tuple[0])
        elif chord_list:
            chord_list.append(chord_list[-1])

    return tuple(c[0] for c in chord_list)


def make_main_pitch_tuple(
    scale_degree, scale, chord_count, chord_ambitus_tuple, random
) -> tuple[music_parameters.JustIntonationPitch, ...]:
    scale_degree_count = len(set(scale.scale_degree_tuple))
    assert scale_degree_count == 5
    if scale_degree == 0:
        main_pitch_cycle = itertools.cycle((0,))
    else:
        low, high = ((scale_degree + n) % scale_degree_count for n in (-1, 1))
        main_pitch_cycle = itertools.cycle((scale_degree, low, scale_degree, high))

    main_pitch_tuple = tuple(
        reversed(
            [
                random.choice(
                    chord_ambitus.get_pitch_variant_tuple(
                        scale.scale_index_to_pitch(next(main_pitch_cycle))
                    )
                )
                for chord_ambitus in chord_ambitus_tuple
            ]
        )
    )
    return main_pitch_tuple


def make_is_chord_harmonic_tuple(chord_count):
    is_chord_harmonic_cycle = itertools.cycle((True, False))
    return tuple(
        reversed(tuple(next(is_chord_harmonic_cycle) for _ in range(chord_count)))
    )


def make_chord_ambitus_tuple(chord_count, random):
    return tuple(random.choice(ambitus_tuple) for _ in range(chord_count))


ambitus_tuple = (
    music_parameters.OctaveAmbitus(
        music_parameters.JustIntonationPitch("3/4"),
        music_parameters.JustIntonationPitch("3/1"),
    ),
    music_parameters.OctaveAmbitus(
        music_parameters.JustIntonationPitch("1/2"),
        music_parameters.JustIntonationPitch("2/1"),
    ),
    music_parameters.OctaveAmbitus(
        music_parameters.JustIntonationPitch("1/1"),
        music_parameters.JustIntonationPitch("4/1"),
    ),
)


def make_pitch_count_tuple(chord_count, random):
    return tuple(random.choice([2, 3, 4]) for _ in range(chord_count))
