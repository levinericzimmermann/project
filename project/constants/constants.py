import ranges

from mutwo import abjad_converters
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import project_parameters

TITLE = "10.2"

diary_interfaces.configurations.DEFAULT_STORAGE_PATH = "etc/data/diary.fs"

SKIP_CHECK = False
SKIP_CHECK_CLOCK = False

# a' frequency
A_FREQUENCY = 442
# we tune to 'a'
music_parameters.configurations.DEFAULT_CONCERT_PITCH = A_FREQUENCY

music_parameters.configurations.EQUAL_DIVIDED_OCTAVE_PITCH_ROUND_FREQUENCY_DIGIT_COUNT = (
    7
)

# Engrave optional notes
abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE = tuple(
    a
    for a in abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE
    if a.__name__ not in ("Tremolo",)
) + (project_parameters.Optional, project_parameters.Tremolo, project_parameters.DurationLine)

SCALE = music_parameters.Scale(
    music_parameters.JustIntonationPitch("1/1"),
    music_parameters.RepeatingScaleFamily(
        [
            music_parameters.JustIntonationPitch(ratio)
            # FIXME: We use only one specific pentatonic subset of the
            # scale for now. Mutwo doesn't offer any good representation
            # of scale with subscales yet so that this is the easiest
            # solution for now.
            # for ratio in "1/1 9/8 7/6 4/3 3/2 12/7 16/9".split(" ")
            for ratio in "1/1 9/8 7/6 3/2 12/7".split(" ")
        ],
        repetition_interval=music_parameters.JustIntonationPitch("2/1"),
        min_pitch_interval=music_parameters.JustIntonationPitch("1/8"),
        max_pitch_interval=music_parameters.JustIntonationPitch("16/1"),
    ),
)

HARP_WRITTEN_SCALE = music_parameters.Scale(
    # Simple minor scale starting from 'c'
    music_parameters.WesternPitch("a", 4),
    music_parameters.RepeatingScaleFamily(
        [
            music_parameters.WesternPitchInterval(pitch)
            for pitch in "p1 m2 m3 p4 p5 m6 m7".split(" ")
        ],
        repetition_interval=music_parameters.JustIntonationPitch("2/1"),
        min_pitch_interval=music_parameters.JustIntonationPitch("1/8"),
        max_pitch_interval=music_parameters.JustIntonationPitch("16/1"),
    ),
)


center = int(len(SCALE.pitch_tuple) // 2)
ORCHESTRATION = music_parameters.Orchestration(
    VIOLIN=project_parameters.Violin(),
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


def sounding_harp_pitch_to_written_harp_pitch(harp_pitch):
    scale_position = SCALE.pitch_to_scale_position(harp_pitch)
    return HARP_WRITTEN_SCALE.scale_position_to_pitch(scale_position)
