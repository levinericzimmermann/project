import dataclasses

from mutwo import diary_interfaces

@dataclasses.dataclass(frozen=True)
class PContext(diary_interfaces.Context, name='project', version=0):
    page_index: int
