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

GATRA_SIZE = 4
GATRA_COUNT = 1

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
)

GENERATOR_INTERVAL_TUPLE = tuple(
    music_parameters.JustIntonationPitch(r)
    for r in "7/6 16/9 4/3 1/1 3/2 9/8 12/7".split(" ")
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

HARP_WRITTEN_SCALE = music_parameters.Scale(
    # Simple minor scale starting from 'a'
    CONCERT_PITCH_WESTERN_PITCH,
    music_parameters.RepeatingScaleFamily(
        [
            music_parameters.WesternPitchInterval(pitch)
            for pitch in "p1 M2 m3 p4 p5 m6 m7".split(" ")
        ],
        repetition_interval=music_parameters.JustIntonationPitch("2/1"),
        min_pitch_interval=music_parameters.JustIntonationPitch("1/16"),
        max_pitch_interval=music_parameters.JustIntonationPitch("16/1"),
    ),
)


center = int(len(SCALE.pitch_tuple) // 2)
ORCHESTRATION = music_parameters.Orchestration(
    V=project_parameters.V(),
    HARP=music_parameters.CelticHarp(pitch_tuple=SCALE.pitch_tuple),
    CLOCK=music_parameters.UnpitchedInstrument("clock", "c"),
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
    ORCHESTRATION_CLOCK.CLOCK_I0: music_parameters.WesternPitch("a", 3),
    ORCHESTRATION_CLOCK.CLOCK_I1: music_parameters.WesternPitch("b", 3),
    ORCHESTRATION_CLOCK.CLOCK_I2: music_parameters.WesternPitch("c", 4),
    ORCHESTRATION_CLOCK.CLOCK_I3: music_parameters.WesternPitch("d", 4),
    ORCHESTRATION_CLOCK.CLOCK_I4: music_parameters.WesternPitch("e", 4),
}

INSTRUMENT_CLOCK_EVENT_TO_PITCHED_CLOCK_EVENT = (
    project_converters.InstrumentNoteLikeToPitchedNoteLike(
        CLOCK_INSTRUMENT_TO_PITCH_DICT
    )
)


def sounding_harp_pitch_to_written_harp_pitch(harp_pitch):
    scale_position = SCALE.pitch_to_scale_position(harp_pitch)
    return HARP_WRITTEN_SCALE.scale_position_to_pitch(scale_position)


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
