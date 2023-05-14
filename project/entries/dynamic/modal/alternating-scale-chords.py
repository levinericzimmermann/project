"""Return harmonies which can be proceeded further.

The basic idea of this entry is that we have two interlocked sequences:

    - a sequence of chords which can't be intonated
    - a sequence of chords which can be intonated

=> 'intonated' means, to be tunable by ear.

The second sequence is based on a scalar interpolation between a
start pitch and an end pitch.

The first sequence is only reacting to the harmony before and after
it from the second sequence.

So we have a structure of

    X   A   X   B   X   C   X   D   ...

where

    X           =       untunable sound
    A/...       =       tunable sound based on scalar interpolation
"""

import functools
import operator

import ranges

from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import project_generators
from mutwo import project_parameters

import project


def is_supported(context, **kwargs):
    try:
        assert isinstance(context, diary_interfaces.ModalContext0)
    except AssertionError:
        return False
    return True


def main(context, scale, **kwargs):
    pitch_tuple = scale(
        diary_interfaces.ModalContext0(
            context.start,
            context.end,
            FAKE_ORCHESTRA,
            modal_event=context.modal_event.copy(),
        ),
        **kwargs
    )

    tunable_chord_tuple = get_tunable_chord_tuple(context, pitch_tuple)
    untunable_chord_tuple = get_untunable_chord_tuple(tunable_chord_tuple)
    return functools.reduce(
        operator.add, zip(untunable_chord_tuple, tunable_chord_tuple)
    )


def get_tunable_chord_tuple(context, pitch_tuple):
    available_pitch_tuple = scale_to_available_pitch_tuple(context.modal_event.scale)
    tunable_chord_list = []
    for p in pitch_tuple:
        champion, fitness = None, None
        for c in project_generators.find_chord_tuple(
            (p.normalize(),),
            available_pitch_tuple,
            pitch_count_range=ranges.Range(2, 4),
        ):
            if not champion or c.harmonicity > fitness:
                champion, fitness = c, c.harmonicity
        chord = champion.pitch_tuple
        tunable_chord_list.append(chord)
    return tuple(tunable_chord_list)


def get_untunable_chord_tuple(tunable_chord_tuple):
    available_pitch_tuple = scale_to_available_pitch_tuple(SCALE)
    untunable_chord_list = []
    for tunable_chord0, tunable_chord1 in zip(
        (tuple([]),) + tunable_chord_tuple, tunable_chord_tuple
    ):
        used_pitch_tuple = tunable_chord0 + tunable_chord1
        unused_pitch_tuple = tuple(
            p for p in available_pitch_tuple if p not in used_pitch_tuple
        )
        untunable_chord_list.append(unused_pitch_tuple)

    return tuple(untunable_chord_list)


def scale_to_available_pitch_tuple(scale):
    return tuple(
        scale.scale_position_to_pitch((d, 0)).normalize(mutate=False)
        for d in range(scale.scale_degree_count)
    )


FAKE_ORCHESTRA = music_parameters.Orchestration(
    I=project_parameters.InfinitePitchedInstrument()
)
SCALE = project.constants.SCALE
