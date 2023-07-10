import typing

from mutwo import core_events
from mutwo import project_generators


class C103Event(core_events.SimpleEvent):
    def __init__(
        self,
        chord: typing.Optional[project_generators.Chord103],
        *args,
        noise_tuple: tuple[bool, bool, bool] = (False, False, False),
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.chord = chord
        self.noise_tuple = noise_tuple

    def attr2noise(self, attr: str) -> bool:
        return bool(
            self.noise_tuple[
                {"tonic": 0, "partner": 1, "written_instable_pitch": 2}[attr]
            ]
        )
