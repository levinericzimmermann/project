import ranges

from mutwo import core_events


__all__ = ("SimultaneousEventWithRepetition", "TaggedSimultaneousEventWithRepetition")


class SimultaneousEventWithRepetition(
    core_events.SimultaneousEvent,
    class_specific_side_attribute_tuple=("repetition_count_range",),
):
    def __init__(self, *args, repetition_count_range=ranges.Range(1, 2), **kwargs):
        super().__init__(*args, **kwargs)
        self.repetition_count_range = repetition_count_range


class TaggedSimultaneousEventWithRepetition(
    core_events.TaggedSimultaneousEvent,
    class_specific_side_attribute_tuple=("repetition_count_range",),
):
    def __init__(self, *args, repetition_count_range=ranges.Range(1, 2), **kwargs):
        super().__init__(*args, **kwargs)
        self.repetition_count_range = repetition_count_range
