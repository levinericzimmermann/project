import collections
import itertools
import typing

import ranges

from mutwo import core_utilities
from mutwo import music_parameters


__all__ = (
    "Chord",
    "ChordDifference",
    "find_chord_tuple",
    "make_chord_difference_tuple",
)


Chord = collections.namedtuple(
    "Chord",
    (
        "pitch_tuple",
        "pitch_count",
        "harmonicity",
        "ambitus",
        "fingering_tuple",
        "interval_tuple",
        "neighbour_interval_tuple",
    ),
)

ChordDifference = collections.namedtuple(
    "ChordDifference",
    (
        "chord0",
        "chord1",
        "intersection",
        "union",
        "only0",
        "only1",
        "intersection_count",
        "interval_tuple",
        "harmonicity",
    ),
)


def make_chord_difference_tuple(
    chord_tuple0: tuple[Chord, ...],
    chord_tuple1: tuple[Chord, ...],
) -> tuple[tuple[Chord, Chord, ChordDifference], ...]:
    """Compute properties of all possible chord sequences between two chord sets"""

    chord_difference_list = []
    for chord0, chord1 in itertools.product(chord_tuple0, chord_tuple1):
        chord_difference_list.append(_make_chord_difference(chord0, chord1))
    return tuple(chord_difference_list)


def _make_chord_difference(chord0: Chord, chord1: Chord):
    union = tuple(
        sorted(core_utilities.uniqify_sequence(chord0.pitch_tuple + chord1.pitch_tuple))
    )
    intersection, only0, only1 = [], [], []
    for p in union:
        if p in chord0.pitch_tuple and p in chord1.pitch_tuple:
            intersection.append(p)
        elif p in chord0.pitch_tuple:
            only0.append(p)
        else:
            only1.append(p)
    interval_tuple = tuple(
        _interval(p0, p1)
        for p0, p1 in itertools.product(chord0.pitch_tuple, chord1.pitch_tuple)
    )
    harmonicity_delta = chord1.harmonicity - chord0.harmonicity
    return ChordDifference(
        chord0,
        chord1,
        tuple(intersection),
        union,
        tuple(only0),
        tuple(only1),
        len(intersection),
        interval_tuple,
        harmonicity_delta,
    )


def find_chord_tuple(
    picked_pitch_tuple: tuple[music_parameters.JustIntonationPitch, ...] = tuple([]),
    pitch_tuple: tuple[music_parameters.JustIntonationPitch, ...] = tuple([]),
    pitch_count_range: ranges.Range = ranges.Range(1, 3),
    min_harmonicity: typing.Optional[float] = music_parameters.JustIntonationPitch(
        "7/4"
    ).harmonicity_simplified_barlow,
    max_harmonicity: typing.Optional[float] = None,
    ambitus: music_parameters.abc.PitchAmbitus = music_parameters.OctaveAmbitus(
        music_parameters.JustIntonationPitch("1/4"),
        music_parameters.JustIntonationPitch("4/1"),
    ),
    instrument: typing.Optional[music_parameters.abc.Instrument] = None,
    min_interval: typing.Optional[music_parameters.abc.PitchInterval] = None,
    max_interval: typing.Optional[music_parameters.abc.PitchInterval] = None,
    **kwargs,
) -> tuple[Chord, ...]:
    """Create a tuple of chords which fulfill specific constraints"""

    valid_pitch_tuple = tuple(
        p for p in pitch_tuple if p in ambitus and p not in picked_pitch_tuple
    )
    picked_pitch_count = len(picked_pitch_tuple)

    chord_list = []
    for pitch_count in range(pitch_count_range.start, pitch_count_range.end):
        if (difference := pitch_count - picked_pitch_count) >= 0:
            for partner_tuple in itertools.combinations(valid_pitch_tuple, difference):
                if chord := _make_chord(
                    picked_pitch_tuple,
                    pitch_count,
                    partner_tuple,
                    min_harmonicity,
                    max_harmonicity,
                    instrument,
                    min_interval,
                    max_interval,
                ):
                    chord_list.append(chord)

    return tuple(chord_list)


def _make_chord(
    picked_pitch_tuple,
    pitch_count,
    partner_pitch_tuple,
    min_harmonicity,
    max_harmonicity,
    instrument,
    min_interval,
    max_interval,
) -> typing.Optional[Chord]:
    harmonicity_list = []
    interval_list = []
    for p0, p1 in tuple(
        itertools.product(picked_pitch_tuple, partner_pitch_tuple)
    ) + tuple(itertools.combinations(partner_pitch_tuple, 2)):
        interval = _interval(p0, p1)
        cents = abs(interval.interval)
        if min_interval and min_interval.interval > cents:
            return
        if max_interval and max_interval.interval < cents:
            return
        harmonicity_list.append(_harmonicity(interval))
        interval_list.append(interval)
    harmonicity = sum(harmonicity_list) / len(harmonicity_list)
    if max_harmonicity and harmonicity > max_harmonicity:
        return
    if min_harmonicity and harmonicity < min_harmonicity:
        return
    pitch_tuple = tuple(sorted(picked_pitch_tuple + partner_pitch_tuple))
    fingering_tuple = None
    if instrument:
        try:
            fingering_tuple = instrument.pitch_sequence_to_fingering_tuple(pitch_tuple)
        except AttributeError:
            pass
        else:
            if not fingering_tuple:
                return
    if len(pitch_tuple) > 1:
        ambitus = music_parameters.OctaveAmbitus(pitch_tuple[0], pitch_tuple[-1])
    else:
        ambitus = music_parameters.OctaveAmbitus(
            pitch_tuple[0], pitch_tuple[0] + music_parameters.JustIntonationPitch("2/1")
        )
    neighbour_interval_list = []
    for p0, p1 in zip(pitch_tuple, pitch_tuple[1:]):
        neighbour_interval_list.append(_interval(p1, p0))
    return Chord(
        pitch_tuple, pitch_count, harmonicity, ambitus, fingering_tuple, tuple(interval_list), tuple(neighbour_interval_list)
    )


# Catch intervals for faster computation
def _interval(p0, p1):
    key = (p0.exponent_tuple, p1.exponent_tuple)
    try:
        return PITCH_TUPLE_TO_INTERVAL[key]
    except KeyError:
        i = PITCH_TUPLE_TO_INTERVAL[key] = p0 - p1
        return i


# Catch harmonicity for faster computation
def _harmonicity(p):
    key = p.exponent_tuple
    try:
        return INTERVAL_TO_HARMONICITY[key]
    except KeyError:
        h = INTERVAL_TO_HARMONICITY[key] = p.harmonicity_simplified_barlow
        return h


PITCH_TUPLE_TO_INTERVAL = {}
INTERVAL_TO_HARMONICITY = {}
