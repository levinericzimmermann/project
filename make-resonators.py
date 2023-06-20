#!/usr/bin/env python

"""Create resonator text files.

For each pentatonic e.g. each page we create three resonators
(because we use 3 different speaker). Resonators use all pitch
classes of the given pentatonic, but with a different accent.

We differentiate in the following manner between pitch classes;

    0           =>      root
    1           =>      most harmonic pitch to root
    2, 3, 4     =>      other pitches, sorted from more to less harmonic
                        (calculated from triad with 0 and 1)

We use the octaves

    -2, -1, 0, 1, 2, 3

    (drop -3 because low sine tones don't seem to fit so well & we
     want an even number of octaves)

Then in each octave there is 0, in every second octave there is 1
and 2, 3 & 4 only appear once in those octaves which aren't populated
by 1 yet, so that we have 2 pitches in each octave. Then we try
to populate this pitch set onto our 3 different speakers with a balanced
& interlocking technique.
"""

import operator
import itertools
import random

random.seed(100)

from mutwo import music_parameters

import project

speaker_count = 3

chord_tuple = (
    (
        # octave, pitch class
        (-2, 0),
        (0, 1),
        (1, 0),
        (3, 2),
    ),
    (
        (-2, 1),
        (-1, 0),
        (1, 3),
        (2, 0),
    ),
    (
        (-1, 4),
        (0, 0),
        (2, 1),
        (3, 0),
    ),
)

pitch_function_to_decibel = (0, -6, -14, -19, -25)
octave_to_decibel_difference = {-2: -12, -1: -6, 0: 0, 1: 0, 2: 0, 3: 0}
pitch_function_to_decay_rate = (0.6, 0.25, 0.125, 0.11, 0.1)
octave_to_decay_rate_factor = {-2: 0.25, -1: 0.5, 0: 0.75, 1: 1, 2: 1, 3: 0.75}


def main():
    chord_order_cycle = itertools.cycle(itertools.permutations(range(speaker_count)))

    for page_index, scale in enumerate(project.constants.PENTATONIC_SCALE_TUPLE):
        pitch_class_tuple = scale_to_pitch_class_tuple(scale)
        chord_order = next(chord_order_cycle)
        for speaker_index, chord_index in enumerate(chord_order):
            chord = chord_tuple[chord_index]
            resonator_configuration = []
            for octave, pitch_function_index in chord:
                pitch = scale.scale_position_to_pitch(
                    (pitch_class_tuple[pitch_function_index], octave)
                )
                resonator_data = pitch_and_function_to_resonator_data(
                    pitch, pitch_function_index, octave
                )
                resonator_configuration.append(resonator_data)
            resonator_configuration_to_file(
                page_index, speaker_index, resonator_configuration
            )


# returns tuple with 5 integers: 0, 1, 2, 3, 4, where
# the order denotes which pitch class has which function
# (first index pitch class is 0, second pitch class index is 1, ...)
def scale_to_pitch_class_tuple(scale):
    root = scale.scale_position_to_pitch((0, 0))
    other = [(n, scale.scale_position_to_pitch((n, 0))) for n in range(1, 5)]
    champion, fitness = None, None
    for i, index_and_p in enumerate(other):
        _, p = index_and_p
        f = (root - p).normalize().harmonicity_simplified_barlow
        if not champion or f > fitness:
            champion, fitness = i, f
    i1, p1 = other[i]
    del other[i]

    dyad = (root, p1)
    remaining = []
    for index, p in other:
        fitness = sum(
            ((p - p_dyad).normalize().harmonicity_simplified_barlow for p_dyad in dyad)
        )
        remaining.append((index, fitness))

    return (0, i1) + tuple(
        index
        for index, _ in sorted(remaining, key=operator.itemgetter(1), reverse=True)
    )


# return (Frequency, Amplitude, DecayRate)
def pitch_and_function_to_resonator_data(pitch, pitch_function_index, octave):
    amplitude = music_parameters.DecibelVolume(
        pitch_function_to_decibel[pitch_function_index]
        + octave_to_decibel_difference[octave]
    ).amplitude
    decay_rate = (
        pitch_function_to_decay_rate[pitch_function_index]
        * random.uniform(0.9, 1.1)
        * octave_to_decay_rate_factor[octave]
    )
    return (
        pitch.frequency,
        amplitude,
        decay_rate,
    )


# Create file
def resonator_configuration_to_file(page_index, speaker_index, resonator_configuration):
    file_path = f"etc/resonators/r_{page_index}_{speaker_index}.txt"
    print(f"write {file_path}...")
    with open(file_path, "w") as resonator_file:
        for partial_index, partial_data in enumerate(resonator_configuration):
            p = f'{partial_index + 1}, {" ".join(map(str, partial_data))};\n'
            resonator_file.write(p)


if __name__ == "__main__":
    main()
