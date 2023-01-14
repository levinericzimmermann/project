import ranges

from mutwo import core_converters
from mutwo import core_events
from mutwo import clock_converters


__all__ = (
    "ClockLineToSimultaneousEvent",
)


class ClockLineToSimultaneousEvent(clock_converters.ClockLineToSimultaneousEvent):
    def _event_placement_to_event(
        self, *args, **kwargs
    ) -> core_events.SimultaneousEvent:
        event = super()._event_placement_to_event(*args, **kwargs)
        d = event.duration
        r = getattr(event, "repetition_count_range", ranges.Range(1, 2))
        repetition_count = self._random.choice(range(r.start, r.end))
        return event.repeat(repetition_count - 1, mutate=False).set("duration", d)
