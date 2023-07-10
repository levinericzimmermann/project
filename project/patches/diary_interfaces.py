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
    # If pitch == None, then we either have a generalpause
    # (all voices are silent), or we only have a rest within our structure
    # (only 1 or 2 voices are silent).
    is_generalpause: bool = False
    # For the generalpause, the context-generator-algorithm decides if
    # the rest should play a noisy texture or not.
    is_noise: bool = False


diary_interfaces.H103Context = H103Context
