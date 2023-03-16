import ranges

from mutwo import core_converters
from mutwo import core_parameters


__all__ = ("AverageNoteDurationToRangePair",)


class AverageNoteDurationToRangePair(core_converters.abc.Converter):
    def convert(
        self,
        average_note_duration: float,
        event_count: int,
        duration_in_seconds: float,
        duration: core_parameters.abc.Duration,
    ) -> tuple[ranges.Range, ranges.Range]:
        expected_full_duration_in_seconds = average_note_duration * event_count
        needed_duration_percentage = (
            expected_full_duration_in_seconds / duration_in_seconds
        )
        if needed_duration_percentage >= 1:
            needed_duration_percentage = 0.95
        remaining = 1 - needed_duration_percentage
        remaining_half = remaining / 2
        start_percentage, end_percentage = (
            remaining_half,
            remaining_half + needed_duration_percentage,
        )
        start_range = ranges.Range(
            duration * start_percentage, duration * (start_percentage * 1.1)
        )
        end_range = ranges.Range(
            duration * (end_percentage * 0.9), duration * end_percentage
        )
        return start_range, end_range
