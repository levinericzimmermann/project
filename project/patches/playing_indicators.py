import dataclasses
import typing

from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_parameters


@dataclasses.dataclass
class BreathIndicator(music_parameters.abc.ImplicitPlayingIndicator):
    breath: typing.Optional[project_parameters.BreathOrHoldBreath] = None


def f(factory=music_parameters.abc.ExplicitPlayingIndicator):
    return dataclasses.field(default_factory=factory)


@dataclasses.dataclass
class PlayingIndicatorCollection(music_parameters.PlayingIndicatorCollection):
    breath_indicator: BreathIndicator = f(BreathIndicator)


music_events.configurations.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS = PlayingIndicatorCollection
