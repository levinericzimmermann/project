import dataclasses

from mutwo import core_events
from mutwo import diary_interfaces


@dataclasses.dataclass(frozen=True)
class PContext(diary_interfaces.Context, name="project", version=0):
    page_index: int
    sentence: str
    melody: core_events.SequentialEvent
    next_melody: core_events.SequentialEvent
