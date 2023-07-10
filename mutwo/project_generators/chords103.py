from __future__ import annotations

import dataclasses
import functools
import itertools
import typing

from mutwo import music_generators
from mutwo import music_parameters

# Special chord-making function for composition 10.3
#
# We only allow 5/4 or 6/5 based triads or
# 3/2 + 9/8 / 4/3 + 16/9 structures.
#
# The thirds/sixth can either be minor or major, both
# is ok (up to the player, musica ficta).
#
# When we have 9/8 it can either be 9/8 or 16/15.
def get_103_chord_tuple(tonic):
    tonic = tonic.normalize(mutate=False)
    j = music_parameters.JustIntonationPitch
    try:
        tonic5comma = tonic.exponent_tuple[2]
    except IndexError:
        tonic5comma = 0
    if tonic5comma == -1:
        ct = (
            _103chord(tonic, j("5/4"), j("3/2"), [], 0),
            _103chord(tonic, j("5/3"), j("4/3"), [], 0),
            _103chord(tonic, j("5/4"), j("16/9"), [], 1),
            _103chord(tonic, j("5/3"), j("9/8"), [], 1),
        )
    elif tonic5comma == 1:
        ct = (
            _103chord(tonic, j("6/5"), j("3/2"), [], 0),
            _103chord(tonic, j("8/5"), j("4/3"), [], 0),
            _103chord(tonic, j("6/5"), j("16/9"), [], 1),
            _103chord(tonic, j("8/5"), j("9/8"), [], 1),
        )
    elif tonic5comma == 0:
        ct = (
            _103chord(tonic, j("3/2"), j("5/4"), (j("6/5"),), 0),
            _103chord(tonic, j("4/3"), j("8/5"), (j("5/3"),), 0),
            _103chord(tonic, j("3/2"), j("9/8"), (j("16/15"),), 1),
            _103chord(tonic, j("4/3"), j("16/9"), (j("15/8"),), 1),
        )
    else:
        raise NotImplementedError(tonic5comma)
    return tuple(p for p in ct if p is not None)


def _103chord(
    tonic, partner_interval, main_instable_interval, instable_interval_tuple, type
) -> typing.Optional[Chord103]:
    partner = (tonic + partner_interval).normalize()
    instable_list = [(tonic + main_instable_interval).normalize()]

    ok = None
    pn0 = instable_list[0].get_closest_pythagorean_pitch_name()
    for instable_interval in instable_interval_tuple:
        p = (instable_interval + tonic).normalize()
        pn1 = p.get_closest_pythagorean_pitch_name()
        # We need to be sure that both pitches are written with the
        # same diatonic pitch, otherwise the 'optional accidental trick'
        # to catch both pitches doesn't work.
        if ok := (pn0[0] == pn1[0]):
            instable_list.append(p)
            break

    # info log
    #
    # if 'ok' is 'None' (so also boolean 'False') it's expected
    # that no second instable pitch could be found (because the
    # chord already doesn't define any alternative), so we don't
    # need to log anything. Only log if iterated and 'False'
    # is the result.
    if ok is False:
        print(
            "no second instable pitch could be found for tonic",
            tonic.ratio,
            "and instable interval",
            main_instable_interval.ratio,
        )

    # The pitch with more accidentals is our written pitch (we explicitly
    # put the accidental into parenthesis, a so-called 'cautionary'
    # accidental).
    #
    # If ok is never set to 'True', this means we never found any
    # pitch from our 'instable_interval_tuple' which has the same
    # diatonic pitch name as the 'main_instable_interval'. In this
    # case we only use an instable pitch set with 1 pitch.
    if not ok or (len(pn0) > len(pn1)):
        written_pitch = instable_list[0]
    else:
        written_pitch = instable_list[1]

    return Chord103.from_pitch_classes(
        tonic, partner, tuple(instable_list), written_pitch, type
    )


@dataclasses.dataclass(frozen=True)
class Chord103(object):
    tonic: music_parameters.JustIntonationPitch
    partner: music_parameters.JustIntonationPitch
    instable_tuple: tuple[
        music_parameters.JustIntonationPitch, music_parameters.JustIntonationPitch
    ] | tuple[music_parameters.JustIntonationPitch]
    written_instable_pitch: music_parameters.JustIntonationPitch
    type: int

    @classmethod
    def from_pitch_classes(
        cls, tonic, partner, instable_tuple, written_instable_pitch, type
    ):
        """If pitches aren't in the right octave yet (e.g. we only deal
        with octave-less pitch-classes), a 'Chord103' should be initialized
        from this method.
        This method moves the pitches to a tunable set.
        """

        written_instable_pitch_index, *_ = tuple(i for i, p in enumerate(instable_tuple) if p == written_instable_pitch)

        tonic_tuple = AMBITUS_DICT["tonic"].get_pitch_variant_tuple(tonic)
        partner_tuple = AMBITUS_DICT["partner"].get_pitch_variant_tuple(partner)
        instable_tuple2 = tuple(
            AMBITUS_DICT["instable"].get_pitch_variant_tuple(instable)
            for instable in instable_tuple
        )

        solution_list_list = []
        for instable_tuple0 in instable_tuple2:
            solution_list = []
            for pitch_tuple in itertools.product(
                tonic_tuple, partner_tuple, instable_tuple0
            ):
                tuneable = True
                fitness_list = []
                for p0, p1 in itertools.combinations(pitch_tuple, 2):
                    if p0 > p1:
                        interval = p0 - p1
                    else:
                        interval = p1 - p0
                    try:
                        difficulty = music_generators.constants.TUNEABLE_INTERVAL_TO_DIFFICULTY_DICT[
                            interval.exponent_tuple
                        ]
                    except KeyError:
                        tuneable = False
                        break
                    else:
                        fitness_list.append(difficulty)
                if tuneable:
                    fitness = sum(fitness_list) / len(pitch_tuple)
                    solution_list.append((pitch_tuple, fitness))
            solution_list_list.append(solution_list)

        # Each entry of 'common_solution_list' is
        #       [TONIC, PARTNER, INSTABLE_TUPLE, FITNESS]
        common_solution_list = []
        if len(solution_list_list) == 1:
            common_solution_list = [
                [s[0][0], s[0][1], [s[0][-1]], s[1]] for s in solution_list_list[0]
            ]
        else:
            for solution_tuple in itertools.product(*solution_list_list):
                pitch_tuple_list = [s[0] for s in solution_tuple]
                is_equal = True
                # :2 => we are only interested in tonic/partner
                for function_pitch_tuple in tuple(zip(*pitch_tuple_list))[:2]:
                    for p0, p1 in zip(function_pitch_tuple, function_pitch_tuple[1:]):
                        if p0 != p1:
                            is_equal = False
                            break
                    if not is_equal:
                        break
                if is_equal:
                    fitness = sum([s[1] for s in solution_tuple]) / len(solution_tuple)
                    pitch_tuple0 = solution_tuple[0][0]
                    instable_pitches = tuple(s[0][-1] for s in solution_tuple)
                    s = [pitch_tuple0[0], pitch_tuple0[1], instable_pitches, fitness]
                    common_solution_list.append(s)

        if not common_solution_list:
            try:
                s0 = min(solution_list_list[0], key=lambda s: s[-1])
            except (ValueError, IndexError):
                print("no solution at all could be found")
                common_solution_list.append(
                    (
                        tonic_tuple[0],
                        partner_tuple[0],
                        tuple(i[0] for i in instable_tuple2),
                        0,
                    )
                )
            else:
                print("no common solution could be found")
                pt = s0[0]
                common_solution_list.append(
                    [
                        pt[0],
                        pt[1],
                        (pt[-1],) + tuple(i[0] for i in instable_tuple2[1:]),
                        0,
                    ]
                )

        tonic, partner, instable_tuple, _ = min(
            common_solution_list, key=lambda s: s[-1]
        )

        return cls(tonic, partner, instable_tuple, instable_tuple[written_instable_pitch_index], type)

    @functools.cached_property
    def pitch_tuple(self) -> tuple[music_parameters.JustIntonationPitch, ...]:
        return (self.tonic, self.partner, self.written_instable_pitch)

    def common_pitch_tuple(
        self, other: Chord103
    ) -> tuple[music_parameters.JustIntonationPitch, ...]:
        return tuple(p for p in self.pitch_tuple if p in other.pitch_tuple)

    def common_pitch_count(self, other: Chord103) -> int:
        return len(self.common_pitch_tuple(other))

    def __hash__(self) -> int:
        return hash(
            (
                self.tonic.exponent_tuple,
                self.partner.exponent_tuple,
                self.written_instable_pitch.exponent_tuple,
            )
        )


j = music_parameters.JustIntonationPitch
AMBITUS_DICT = {
    "tonic": music_parameters.OctaveAmbitus(j("3/5"), j("3/2")),
    "partner": music_parameters.OctaveAmbitus(j("3/4"), j("15/8")),
    "instable": music_parameters.OctaveAmbitus(j("15/16"), j("5/2")),
}
