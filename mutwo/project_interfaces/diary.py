import dataclasses
import typing

from mutwo import diary_interfaces
from mutwo import music_parameters


@dataclasses.dataclass(frozen=True)
class ProjectContext(diary_interfaces.Context):
    tonic: music_parameters.JustIntonationPitch = music_parameters.JustIntonationPitch(
        "1/1"
    )
    previous_tonic: typing.Optional[music_parameters.JustIntonationPitch] = None
    next_tonic: typing.Optional[music_parameters.JustIntonationPitch] = None
