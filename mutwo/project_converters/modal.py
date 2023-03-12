import itertools
import typing

import yamm

from mutwo import core_converters
from mutwo import music_parameters

__all__ = ("ScaleToGatraTuple", "GatraTupleToMarkovChain")

# ########################################
# BEGIN copied from 'music_parameters/scales.py'
ScaleDegree: typing.TypeAlias = int
PeriodRepetitionCount: typing.TypeAlias = int
ScalePosition: typing.TypeAlias = tuple[ScaleDegree, PeriodRepetitionCount]
# END
# ########################################

Gatra: typing.TypeAlias = tuple[
    ScalePosition, ScalePosition, ScalePosition, ScalePosition
]
"""A line/bar composed of four different pitches.

The term 'gatra' is borrowed from Javanese Karawitan. It denotes
a sequence of four pitches, where - according to the ding/dong principle -
the second and the fourth tones are stressed (e.g. more important than the
first and the third tone).
"""

# This dict denotes allowed movements from a given scale degree
# to another scale degree in a pentatonic scale.
#
# 0 can move anywhere, and any pitch can move to 0, because it's
# the tonic.
#
# All other scale degrees are only allowed to move to their neighbours
# or to 0. If one of their neighbour is already 0, they only have two
# options where they can move.
VALID_MOVEMENT_DICT = {
    0: {1, 2, 3, 4},
    1: {0, 2},
    2: {0, 1, 3},
    3: {0, 2, 4},
    4: {0, 3},
}


class ScaleToGatraTuple(core_converters.abc.Converter):
    """Find all valid gatra in a pentatonic scale.

    The idea is to use those gatra, combine them to a longer sequence
    of scale positions and finally create ModalContext events from this
    sequence to create a 'Clock' and the related music.

    I use the reference of gatra to denote a sequence of pitches
    which follow predefined rules and a notion of stressed vs. not
    stressed positions.

    The basic idea of those predefined rules is to create a music which
    centers around a main pitch pair. This music is not about development,
    tension or movement, but rather about the absence of those:
    It's really just a subtle variation of a drone.
    """

    # Only for pentatonic scales
    SCALE_SIZE = 5

    def convert(self, scale: music_parameters.Scale) -> tuple[Gatra, ...]:
        assert len(set(scale.scale_family.scale_degree_tuple)) == self.SCALE_SIZE
        dominant_scale_degree = self._find_dominant_scale_degree(scale)
        main_scale_degree_tuple = (0, dominant_scale_degree)
        scale_degree_tuple = tuple(range(self.SCALE_SIZE))
        gatra_list = []
        for candidate in itertools.product(
            scale_degree_tuple,
            main_scale_degree_tuple,
            scale_degree_tuple,
            main_scale_degree_tuple,
        ):
            is_illegal = False
            for s0, s1 in zip(candidate, candidate[1:]):
                if is_illegal := (s1 not in VALID_MOVEMENT_DICT[s0]):
                    break
            if is_illegal:
                continue
            scale_position_tuple = tuple(
                (scale_degree, 0) for scale_degree in candidate
            )
            gatra_list.append(scale_position_tuple)
        return tuple(gatra_list)  # type: ignore

    def _find_dominant_scale_degree(self, scale: music_parameters.Scale) -> int:
        main = scale.scale_position_to_pitch((0, 0))
        champion, fitness = 0, 0
        for candidate in range(1, self.SCALE_SIZE):
            pcandidate = scale.scale_position_to_pitch((candidate, 0))
            h = (main - pcandidate).harmonicity_simplified_barlow
            if h > fitness:
                champion, fitness = candidate, h
        assert champion != 0
        return champion


class GatraTupleToMarkovChain(core_converters.abc.Converter):
    def convert(self, gatra_tuple: tuple[Gatra, ...]) -> yamm.chain.Chain:
        d = {(g,): {} for g in gatra_tuple}
        for gatra_pair in itertools.combinations(gatra_tuple, 2):
            for g0, g1 in itertools.permutations(gatra_pair):
                if g1[0][0] in VALID_MOVEMENT_DICT[g0[-1][0]]:
                    d[(g0,)][g1] = 1
        return yamm.chain.Chain(d)
