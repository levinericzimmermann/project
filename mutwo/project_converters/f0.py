from mutwo import core_converters
from mutwo import core_utilities


class EventToF0(core_converters.abc.EventConverter):
    PARAMETER_DELIMITER = ","
    EVENT_DELIMITER = "\n"

    def convert(self, event_to_convert):
        return self._convert_event(event_to_convert, 0)[0]

    def _convert_simple_event(self, event_to_convert, absolute_entry_delay):
        e = event_to_convert

        d = int(round(float(e.duration) * 1000))

        try:
            v = e.volume.midi_velocity
        except AttributeError:
            v = 0
        else:
            v = int(core_utilities.scale(v, 0, 127, 0, 255))

        try:
            f = round(e.pitch_list[0].frequency * 2, 2)
        except (AttributeError, IndexError):
            f = 0

        # duration,frequency,velocity
        return (self.PARAMETER_DELIMITER.join([str(p) for p in (d, f, v)]),)

    def _convert_sequential_event(self, *args, **kwargs):
        return (
            self.EVENT_DELIMITER.join(
                super()._convert_sequential_event(*args, **kwargs)
            ),
        )

    def _convert_simultaneous_event(
        self,
        e,
        absolute_entry_delay,
        depth,
    ):
        if (ecount := len(e)) == 1:
            return self._convert_event(e[0], absolute_entry_delay, depth)
        elif ecount == 0:
            return tuple([])
        raise NotImplementedError("f0 doesn't support simultaneous events!")
