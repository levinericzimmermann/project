import walkmanio

from mutwo import core_converters
from mutwo import core_events


__all__ = ("SequentialEventToWalkmanEventTuple",)


class SequentialEventToWalkmanEventTuple(core_converters.abc.Converter):
    def convert(
            self, event_to_convert: core_events.SequentialEvent, is_string: bool=True
    ) -> tuple[walkmanio.WalkmanEvent, ...]:
        e_list = []
        for event in event_to_convert:
            is_rest = not (hasattr(event, "pitch_list") and event.pitch_list)
            duration = float(event.duration.duration)
            kwargs = {}
            if not is_rest and is_string:
                kwargs["frequency"] = event.pitch_list[0].frequency * getattr(
                    event, "frequency_factor", 1
                )
                kwargs["envelope"] = getattr(event, "envelope", "basic")
            e = walkmanio.WalkmanEvent(duration, kwargs, is_rest)
            e_list.append(e)
        return tuple(e_list)
