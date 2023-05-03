import dataclasses
import typing

from mutwo import music_events
from mutwo import music_parameters

music_parameters_NotationIndicatorCollection = (
    music_parameters.NotationIndicatorCollection
)


@dataclasses.dataclass
class RhythmicInformation(music_parameters.abc.NotationIndicator):
    activity: bool = False

@dataclasses.dataclass
class FlagStrokeStyle(music_parameters.abc.NotationIndicator):
    style: typing.Optional[str] = None


@dataclasses.dataclass
class NotationIndicatorCollection(music_parameters_NotationIndicatorCollection):
    duration_line: music_parameters.abc.ExplicitPlayingIndicator = dataclasses.field(
        default_factory=music_parameters.abc.ExplicitPlayingIndicator
    )
    flag_stroke_style: FlagStrokeStyle = dataclasses.field(
        default_factory=FlagStrokeStyle
    )
    rhythmic_information: RhythmicInformation = dataclasses.field(
        default_factory=lambda: RhythmicInformation(activity=False)
    )


music_parameters.NotationIndicatorCollection = NotationIndicatorCollection
music_events.configurations.DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS = (
    NotationIndicatorCollection
)
