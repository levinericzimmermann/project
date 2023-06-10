from __future__ import annotations

import dataclasses
import functools

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
    return (
        _103chord(tonic, j("3/2"), j("5/4"), (j("6/5"),), 0),
        _103chord(tonic, j("4/3"), j("8/5"), (j("5/3"),), 0),
        _103chord(tonic, j("3/2"), j("9/8"), (j("16/15"),), 1),
        _103chord(tonic, j("4/3"), j("16/9"), (j("15/8"),), 1),
    )


def _103chord(
    tonic, partner_interval, main_instable_interval, instable_interval_tuple, type
):
    partner = (tonic + partner_interval).normalize()
    instable_list = [(tonic + main_instable_interval).normalize()]
    pn0 = instable_list[0].get_closest_pythagorean_pitch_name()
    for instable_interval in instable_interval_tuple:
        p = instable_interval + tonic
        pn1 = p.get_closest_pythagorean_pitch_name()
        # We need to be sure that both pitches are written with the
        # same diatonic pitch, otherwise the 'optional accidental trick'
        # to catch both pitches doesn't work.
        if ok := (pn0[0] == pn1[0]):
            instable_list.append(p)
            break

    # info log
    if not ok:
        print(
            "no second instable pitch could be found for tonic",
            tonic,
            "and instable interval",
            main_instable_interval,
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

    return Chord103(tonic, partner, tuple(instable_list), written_pitch, type)


@dataclasses.dataclass(frozen=True)
class Chord103(object):
    tonic: music_parameters.JustIntonationPitch
    partner: music_parameters.JustIntonationPitch
    instable_tuple: tuple[
        music_parameters.JustIntonationPitch, music_parameters.JustIntonationPitch
    ] | tuple[music_parameters.JustIntonationPitch]
    written_instable_pitch: music_parameters.JustIntonationPitch
    type: int

    @functools.cached_property
    def pitch_tuple(self) -> tuple[music_parameters.JustIntonationPitch, ...]:
        return (self.tonic, self.partner, self.written_instable_pitch)

    def common_pitch_tuple(
        self, other: Chord103
    ) -> tuple[music_parameters.JustIntonationPitch, ...]:
        return tuple(p for p in self.pitch_tuple if p in other.pitch_tuple)

    def common_pitch_count(self, other: Chord103) -> int:
        return len(self.common_pitch_tuple(other))
