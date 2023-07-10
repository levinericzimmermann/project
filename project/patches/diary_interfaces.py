import dataclasses
import typing

from mutwo import diary_interfaces
from mutwo import music_parameters


@dataclasses.dataclass(frozen=True)
class H103Context(diary_interfaces.CommonContext, name="h103", version=0):
    attr: str = "tonic"
    pitch: typing.Optional[music_parameters.JustIntonationPitch] = None
    # Other pitches of the chord
    other_pitch_tuple: tuple[music_parameters.JustIntonationPitch, ...] = tuple([])
    # Alternative intonations for our current pitch
    alternative_pitch_tuple: tuple[music_parameters.JustIntonationPitch, ...] = tuple(
        []
    )


diary_interfaces.H103Context = H103Context
