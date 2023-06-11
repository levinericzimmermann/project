import dataclasses
import enum
import functools


class Translator(enum.Enum):
    BARNARD = "Mary Barnard"
    RAYOR = "Diane J. Rayor, André Lardinois"


@dataclasses.dataclass(frozen=True)
class Poem(object):
    name: str
    text: str
    translator: Translator = Translator.BARNARD

    @functools.cached_property
    def line_tuple(self) -> tuple[str, ...]:
        return tuple(self.text.split("\n"))
