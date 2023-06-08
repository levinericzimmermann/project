from mutwo import abjad_converters
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import project_parameters

TITLE = "10.3"

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
    project_parameters.SynchronizationPoint,
    project_parameters.Bridge,
    project_parameters.MovingOverpressure,
    project_parameters.BowedBox,
    project_parameters.ExplicitFermata,
)
