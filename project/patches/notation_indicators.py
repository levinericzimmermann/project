import dataclasses

from mutwo import music_events
from mutwo import music_parameters

music_parameters_NotationIndicatorCollection = (
    music_parameters.NotationIndicatorCollection
)


@dataclasses.dataclass
class NotationIndicatorCollection(music_parameters_NotationIndicatorCollection):
    duration_line: music_parameters.abc.ExplicitPlayingIndicator = dataclasses.field(
        default_factory=music_parameters.abc.ExplicitPlayingIndicator
    )


music_parameters.NotationIndicatorCollection = NotationIndicatorCollection
music_events.configurations.DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS = NotationIndicatorCollection
