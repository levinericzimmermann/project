import typing

from mutwo import core_events
from mutwo import project_generators


class C103Event(core_events.SimpleEvent):
    def __init__(
        self, chord: typing.Optional[project_generators.Chord103], *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.chord = chord
