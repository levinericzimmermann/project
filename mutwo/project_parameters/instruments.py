import dataclasses
import itertools

import ranges

from mutwo import music_parameters
from mutwo import project_parameters

from mutwo.music_parameters.instruments.general import _setdefault


__all__ = ("Violin", "AeolianHarp")


class Violin(music_parameters.ContinuousPitchedStringInstrument):
    def __init__(self, **kwargs):
        super().__init__(
            **_setdefault(kwargs, project_parameters.configurations.DEFAULT_VIOLIN_DICT)
        )


class AeolianHarp(music_parameters.DiscreetPitchedStringInstrument):
    # My aeolian harp is actually build of three independent instrument
    # parts. Each part has 3 strings.
    # Because of the specific construction (the position of the pickup and
    # the frets) each box only has an ambitus of a 3/2.
    # To still be able to play all pitches in an octave we slightly
    # detune the three boxes from each other:
    #
    # - The first box is 32/27 deeper
    # - The third box is 9/8 higher
    #
    # In the code we represent this with our adhoc "AeolianHarpBox" class.
    @dataclasses.dataclass(frozen=True)
    class AeolianHarpBox(object):
        ambitus: music_parameters.OctaveAmbitus

    AEOLIAN_HARP_BOX_TUPLE = (
        AeolianHarpBox(
            music_parameters.OctaveAmbitus(
                music_parameters.JustIntonationPitch("27/32"),
                music_parameters.JustIntonationPitch("81/64"),
            )
        ),
        AeolianHarpBox(
            music_parameters.OctaveAmbitus(
                music_parameters.JustIntonationPitch("1/1"),
                music_parameters.JustIntonationPitch("3/2"),
            )
        ),
        AeolianHarpBox(
            music_parameters.OctaveAmbitus(
                music_parameters.JustIntonationPitch("9/8"),
                music_parameters.JustIntonationPitch("27/16"),
            )
        ),
    )

    BOX_STRING_COUNT = 3
    BOX_COUNT = len(AEOLIAN_HARP_BOX_TUPLE)
    TOTAL_STRING_COUNT = BOX_COUNT * BOX_STRING_COUNT

    def __init__(self, pitch_tuple: tuple[music_parameters.JustIntonationPitch, ...]):
        # We need to distribute the pitch tuple on our strings.
        # There are most likely multiple possible solutions how to distribute the pitch tuple.
        # But not all of them are valid.
        # Only those are valid which:
        #
        #   - encompass all pitches
        #   - encompass all strings
        #
        # We first calculate for each pitch a tuple which describes
        # on which boxes we could potentially move this pitch to.
        valid_box_combination_list = []
        for pitch in pitch_tuple:
            valid_box_index_list = []
            s_count = 1
            for bindex, b in enumerate(self.AEOLIAN_HARP_BOX_TUPLE):
                if pitch_variant_tuple := b.ambitus.get_pitch_variant_tuple(pitch):
                    valid_box_index_list.append((bindex, pitch_variant_tuple[0]))
                    s_count += 1
            # We immediately append all possible combinations:
            # if a pitch fits on multiple boxes, this pitch can appear
            # on one box (which one?) or on multiple of the available boxes.
            valid_box_combinations = []
            for k in range(1, s_count):
                for c in itertools.combinations(valid_box_index_list, k):
                    valid_box_combinations.append(c)
            valid_box_combination_list.append(tuple(valid_box_combinations))
        # Now we iterate through all potential modes.
        # As soon as we find a valid solution we stop to make the algorithm
        # fast (and we don't really care about which solution we take :).
        for solution_attempt in itertools.product(*valid_box_combination_list):
            box_list = [[] for _ in self.AEOLIAN_HARP_BOX_TUPLE]
            for pitch_data in solution_attempt:  # Encompass all pitches
                for bindex, pitch in pitch_data:
                    box_list[bindex].append(pitch)
            # Encompass all strings
            if all((len(b) == self.BOX_STRING_COUNT for b in box_list)):
                solution = box_list
                break
        # Now we found a solution and we can simply build our strings and prepare
        # for initialization.
        string_list = []
        pitch_list = []
        string_index = 0
        for box in solution:
            for pitch in sorted(box):
                string_list.append(music_parameters.String(string_index, pitch))
                pitch_list.append(pitch)
                string_index += 1
        super().__init__(
            tuple(pitch_list),
            name="aeolian harp",
            short_name="a.h",
            string_tuple=tuple(string_list),
            pitch_count_range=ranges.Range(1, self.TOTAL_STRING_COUNT + 1)
        )

    # Aeolian harp doesn't support harmonics!
    def get_harmonic_pitch_variant_tuple(self, *args, **kwargs):
        return tuple()
