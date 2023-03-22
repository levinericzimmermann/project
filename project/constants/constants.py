import ranges

from mutwo import abjad_converters
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import project_parameters

TITLE = "10.1"

WALKMAN_DATA_PATH = "etc/walkmansequences"
diary_interfaces.configurations.DEFAULT_STORAGE_PATH = "etc/data/diary.fs"

SKIP_CHECK = False
SKIP_CHECK_CLOCK = False

# a' frequency
A_FREQUENCY = 440
A_3_FREQUENCY = A_FREQUENCY / 2
# we tune to 'a'
music_parameters.configurations.DEFAULT_CONCERT_PITCH = A_3_FREQUENCY

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
