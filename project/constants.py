import dataclasses
import functools
import typing

import ranges

from mutwo import abjad_converters
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import project_converters
from mutwo import project_parameters

TITLE = "10.2"

# Hard-coded: as many pages as lines in the lax poem.
PAGE_COUNT = 16

# Poem by robert lax.
# Foundation of this composition.
POEM = r"""river
river
river

river
river
river

river
river
river

river
river
river
"""

assert len(POEM.split("\n")) == PAGE_COUNT

GATRA_COUNT = 3

SCALE_INDEX_TUPLE = (
    # Pentatonics.
    # Scale indices, but as their generator index from 1 to 7.
    # First number is the index of the tonic.
    #
    # Based on the following grid:
    #
    #   1   7   6   5       river
    #   7   6   5   4       river
    #   6   5   4   3       river
    #   5   4   3   2
    #
    12567,
    71456,
    67145,
    56234,
    71456,
    67345,
    56734,
    45623,
    67145,
    56734,
    45623,
    34562,
    51234,
    45673,
    34562,
    23451,
)

assert len(SCALE_INDEX_TUPLE) == PAGE_COUNT

diary_interfaces.configurations.DEFAULT_STORAGE_PATH = "etc/data/diary.fs"

SKIP_CHECK = False
SKIP_CHECK_CLOCK = False

# a' frequency
A_FREQUENCY = 442
# we tune to 'a'
music_parameters.configurations.DEFAULT_CONCERT_PITCH = A_FREQUENCY
CONCERT_PITCH_WESTERN_PITCH = music_parameters.WesternPitch("a", 4)
CONCERT_PITCH_JUST_INTONATION_PITCH = music_parameters.JustIntonationPitch("1/1")

music_parameters.configurations.EQUAL_DIVIDED_OCTAVE_PITCH_ROUND_FREQUENCY_DIGIT_COUNT = (
    7
)

# Engrave optional notes
abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE = tuple(
    a
    for a in abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE
    if a.__name__ not in ("Tremolo",)
) + (
    project_parameters.Optional,
    project_parameters.Tremolo,
    project_parameters.DurationLine,
    project_parameters.Cluster,
    project_parameters.SonsXylo,
    project_parameters.Flageolet,
    project_parameters.RhythmicInformation,
    project_parameters.FlagStrokeStyle,
    project_parameters.NoteHead,
)

GENERATOR_INTERVAL_TUPLE = tuple(
    music_parameters.JustIntonationPitch(r)
    for r in "7/6 9/5 4/3 1/1 3/2 10/9 12/7".split(" ")
)

# We need to use special intervals for the Glockenspiel,
# because we can only tune it down: this means some intervals
# are very off compared to the intervals of the other instruments.
# But that's fine: semantically it's still the same.
GLOCKENSPIEL_GENERATOR_INTERVAL_TUPLE = tuple(
    music_parameters.JustIntonationPitch(r)
    for r in "7/6 9/5 4/3 1/1 3/2 10/9 12/7".split(" ")
)

assert len(GENERATOR_INTERVAL_TUPLE) == 7

# Global tuning based scale. Similar to 'pelog', because
# we never use all 7 pitches, but only pentatonic subsets.
SCALE = music_parameters.Scale(
    CONCERT_PITCH_JUST_INTONATION_PITCH,
    music_parameters.RepeatingScaleFamily(
        tuple(sorted(GENERATOR_INTERVAL_TUPLE)),
        repetition_interval=music_parameters.JustIntonationPitch("2/1"),
        min_pitch_interval=music_parameters.JustIntonationPitch("1/16"),
        max_pitch_interval=music_parameters.JustIntonationPitch("16/1"),
    ),
)

HARP_AMBITUS = music_parameters.OctaveAmbitus(
    music_parameters.JustIntonationPitch("1/8"),
    music_parameters.JustIntonationPitch("7/1"),
)

GLOCKENSPIEL_AMBITUS = music_parameters.OctaveAmbitus(
    music_parameters.JustIntonationPitch("1/2"),
    music_parameters.JustIntonationPitch("1/1"),
)

GLOCKENSPIEL_SCALE = music_parameters.Scale(
    CONCERT_PITCH_JUST_INTONATION_PITCH,
    music_parameters.RepeatingScaleFamily(
        tuple(sorted(GLOCKENSPIEL_GENERATOR_INTERVAL_TUPLE)),
        repetition_interval=music_parameters.JustIntonationPitch("2/1"),
        min_pitch_interval=GLOCKENSPIEL_AMBITUS.minima_pitch,
        max_pitch_interval=GLOCKENSPIEL_AMBITUS.maxima_pitch,
    ),
)

RETUNED_INSTRUMENT_INTERVAL_TUPLE = tuple(
    music_parameters.WesternPitchInterval(pitch)
    for pitch in "p1 M2 m3 p4 p5 M6 m7".split(" ")
)

# Two simple minor scales starting from 'a'


HARP_SCALE = music_parameters.Scale(
    CONCERT_PITCH_JUST_INTONATION_PITCH,
    music_parameters.RepeatingScaleFamily(
        tuple(sorted(GENERATOR_INTERVAL_TUPLE)),
        repetition_interval=music_parameters.JustIntonationPitch("2/1"),
        min_pitch_interval=HARP_AMBITUS.minima_pitch,
        max_pitch_interval=HARP_AMBITUS.maxima_pitch,
    ),
)

HARP_WRITTEN_SCALE = music_parameters.Scale(
    CONCERT_PITCH_WESTERN_PITCH,
    music_parameters.RepeatingScaleFamily(
        RETUNED_INSTRUMENT_INTERVAL_TUPLE,
        repetition_interval=music_parameters.WesternPitchInterval("p8"),
        min_pitch_interval=HARP_AMBITUS.minima_pitch,
        max_pitch_interval=HARP_AMBITUS.maxima_pitch,
    ),
)

GLOCKENSPIEL_WRITTEN_SCALE = music_parameters.Scale(
    CONCERT_PITCH_WESTERN_PITCH,
    music_parameters.RepeatingScaleFamily(
        RETUNED_INSTRUMENT_INTERVAL_TUPLE,
        repetition_interval=music_parameters.WesternPitchInterval("p8"),
        min_pitch_interval=GLOCKENSPIEL_AMBITUS.minima_pitch,
        max_pitch_interval=GLOCKENSPIEL_AMBITUS.maxima_pitch,
    ),
)


center = int(len(SCALE.pitch_tuple) // 2)
ORCHESTRATION = music_parameters.Orchestration(
    V=project_parameters.V(),
    HARP=music_parameters.CelticHarp(pitch_tuple=HARP_SCALE.pitch_tuple),
    GLOCKENSPIEL=music_parameters.DiscreetPitchedInstrument(
        name="glockenspiel", short_name="g.", pitch_tuple=GLOCKENSPIEL_SCALE.pitch_tuple
    ),
    CLOCK=music_parameters.UnpitchedInstrument("clock", "c"),
    PCLOCK=music_parameters.UnpitchedInstrument("pclock", "pc"),
)

CLOCK_INSTRUMENT_COUNT = 5

ORCHESTRATION_CLOCK = music_parameters.Orchestration(
    **{
        f"CLOCK_I{index}": music_parameters.UnpitchedInstrument(
            f"c{index}", f"c{index}"
        )
        for index in range(CLOCK_INSTRUMENT_COUNT)
    }
)

CLOCK_INSTRUMENT_TO_PITCH_DICT = {
    ORCHESTRATION_CLOCK.CLOCK_I0: music_parameters.WesternPitch("g", 3),
    ORCHESTRATION_CLOCK.CLOCK_I1: music_parameters.WesternPitch("a", 3),
    ORCHESTRATION_CLOCK.CLOCK_I2: music_parameters.WesternPitch("b", 3),
    ORCHESTRATION_CLOCK.CLOCK_I3: music_parameters.WesternPitch("c", 4),
    ORCHESTRATION_CLOCK.CLOCK_I4: music_parameters.WesternPitch("d", 4),
}

INSTRUMENT_CLOCK_EVENT_TO_PITCHED_CLOCK_EVENT = (
    project_converters.InstrumentNoteLikeToPitchedNoteLike(
        CLOCK_INSTRUMENT_TO_PITCH_DICT
    )
)


def sounding_harp_pitch_to_written_harp_pitch(harp_pitch):
    return _sounding_pitch_to_written_pitch(harp_pitch, HARP_SCALE, HARP_WRITTEN_SCALE)


def sounding_glockenspiel_pitch_to_written_glockenspiel_pitch(p):
    return _sounding_pitch_to_written_pitch(
        p, GLOCKENSPIEL_SCALE, GLOCKENSPIEL_WRITTEN_SCALE
    )


def _sounding_pitch_to_written_pitch(pitch, sounding_scale, written_scale):
    try:
        scale_position = sounding_scale.pitch_to_scale_position(pitch)
        return written_scale.scale_position_to_pitch(scale_position)
    except Exception as e:
        print(str(e))
        return pitch


def _make_pentatonic_scale_tuple():
    scale_list = []
    for scale_index in SCALE_INDEX_TUPLE:
        indices = (int(n) - 1 for n in str(scale_index))
        interval_tuple = tuple(GENERATOR_INTERVAL_TUPLE[i] for i in indices)
        main_pitch, *_ = interval_tuple

        ref_pitch = music_parameters.JustIntonationPitch("1/1")

        interval_list = []
        for p in interval_tuple:
            i = p - main_pitch
            while i < ref_pitch:
                i += music_parameters.JustIntonationPitch("2/1")
            interval_list.append(i)

        interval_list = sorted(interval_list)

        scale = music_parameters.Scale(
            CONCERT_PITCH_JUST_INTONATION_PITCH + main_pitch,
            music_parameters.RepeatingScaleFamily(
                interval_list,
                repetition_interval=music_parameters.JustIntonationPitch("2/1"),
                min_pitch_interval=music_parameters.JustIntonationPitch("1/8"),
                max_pitch_interval=music_parameters.JustIntonationPitch("16/1"),
            ),
        )
        scale_list.append(scale)
    return tuple(scale_list)


PENTATONIC_SCALE_TUPLE = _make_pentatonic_scale_tuple()


@dataclasses.dataclass(frozen=True)
class VKlang(object):
    scale_degree: int
    main_string_index: int
    side_string_index: int
    main_string_pitch: typing.Optional[music_parameters.JustIntonationPitch] = None
    side_string_pitch: typing.Optional[music_parameters.JustIntonationPitch] = None
    is_side_string_optional: bool = False

    def __post_init__(self):
        if self.main_string_pitch is None:
            object.__setattr__(
                self,
                "main_string_pitch",
                ORCHESTRATION.V.string_tuple[self.main_string_index].tuning,
            )
        if self.side_string_pitch is None:
            object.__setattr__(
                self,
                "side_string_pitch",
                ORCHESTRATION.V.string_tuple[self.side_string_index].tuning,
            )

    @functools.cached_property
    def is_stable(self) -> bool:
        return self.main_string_pitch in SCALE.pitch_tuple


j = music_parameters.JustIntonationPitch

ORCHESTRATION.V.v_klang_tuple = (
    VKlang(2, 0, 1),
    VKlang(3, 0, 1, j("1/6"), music_parameters.JustIntonationPitch("2/9")),
    VKlang(4, 0, 1, j("3/16")),
    VKlang(5, 0, 1, j("7/36"), music_parameters.JustIntonationPitch("2/9")),
    VKlang(6, 0, 1, j("9/40")),
    VKlang(6, 1, 0),
    VKlang(0, 1, 0, j("1/4")),
    VKlang(0, 1, 2, j("1/4")),
    VKlang(1, 1, 2, j("5/18"), j("3/8")),
    VKlang(2, 1, 2, j("7/24")),
    VKlang(3, 1, 2, j("1/3")),
    VKlang(3, 2, 1),
    VKlang(3, 2, 3),
    VKlang(4, 2, 3, j("3/8")),
    VKlang(5, 2, 3, j("3/7")),
    VKlang(6, 2, 3, j("9/20")),
    VKlang(0, 2, 3, j("1/2")),
    VKlang(0, 3, 2),
    VKlang(1, 3, 2, j("5/9")),  # XXX: Dissonant interval!
    VKlang(2, 3, 2, j("7/12")),
    VKlang(3, 3, 2, j("2/3")),
)
