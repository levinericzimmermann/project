import dataclasses
import enum

from mutwo import music_events
from mutwo import music_parameters

music_parameters_Tremolo = music_parameters.Tremolo


@dataclasses.dataclass()
class Tremolo(music_parameters_Tremolo):
    class D(enum.Enum):
        Stable = ""
        Acc = "tr. acc."
        Rit = "tr. rit."
        AccRit = "tr. acc. <> rit."
        RitAcc = "tr. rit. <> acc."

    # Can be
    #   - None
    #   - 'tremolo acc.'
    #   - 'tremolo rit.'
    #   - 'tremolo acc. + rit.'
    #   - 'tremolo rit. + acc.'
    dynamic: D = D.Stable


music_parameters.Tremolo = Tremolo

music_parameters_PlayingIndicatorCollection = (
    music_parameters.PlayingIndicatorCollection
)


@dataclasses.dataclass
class PlayingIndicatorCollection(music_parameters_PlayingIndicatorCollection):
    cluster: music_parameters.abc.PlayingIndicator = dataclasses.field(
        default_factory=music_parameters.abc.ExplicitPlayingIndicator
    )


music_parameters.PlayingIndicatorCollection = PlayingIndicatorCollection
music_events.configurations.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS = (
    PlayingIndicatorCollection
)
