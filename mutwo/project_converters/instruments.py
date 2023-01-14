from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters


class InstrumentNoteLikeToPitchedNoteLike(
    core_converters.abc.SymmetricalEventConverter
):
    def __init__(self, instrument_to_pitch_dict):
        self.instrument_to_pitch_dict = instrument_to_pitch_dict

    def _convert_simple_event(self, event_to_convert, absolute_time):
        try:
            event_to_convert.grace_note_sequential_event = self.convert(
                event_to_convert.grace_note_sequential_event
            )
        except AttributeError:
            pass

        try:
            event_to_convert.after_grace_note_sequential_event = self.convert(
                event_to_convert.after_grace_note_sequential_event
            )
        except AttributeError:
            pass

        instrument_list = getattr(event_to_convert, "instrument_list", None)
        instrument_list = getattr(event_to_convert, "instrument_list", None)
        if instrument_list is not None and len(instrument_list):
            pitch_list = [
                self.instrument_to_pitch_dict[instrument]
                for instrument in instrument_list
            ]
            return event_to_convert.copy().set_parameter("pitch_list", pitch_list)
        return event_to_convert

    def convert(self, event_to_convert):
        return self._convert_event(event_to_convert, core_parameters.DirectDuration(0))


class SoundingNoteLikeToWrittenNoteLike(core_converters.abc.SymmetricalEventConverter):
    def __init__(self, sounding_pitch_to_written_pitch):
        self.sounding_pitch_to_written_pitch = sounding_pitch_to_written_pitch

    def _convert_simple_event(self, event_to_convert, absolute_time):
        pitch_list = getattr(event_to_convert, "pitch_list", None)
        if pitch_list is not None:
            pitch_list = [
                self.sounding_pitch_to_written_pitch(pitch) for pitch in pitch_list
            ]
            return event_to_convert.set_parameter("pitch_list", pitch_list, mutate=True)
        return event_to_convert

    def convert(self, event_to_convert):
        return self._convert_event(event_to_convert, core_parameters.DirectDuration(0))


class FilterPizzicatoNoteLike(core_converters.abc.SymmetricalEventConverter):
    def _convert_simple_event(self, event_to_convert, absolute_time):
        if (
            c := getattr(event_to_convert, "playing_indicator_collection", None)
        ) and c.string_contact_point.contact_point != "pizzicato":
            return core_events.SimpleEvent(event_to_convert.duration)
        return event_to_convert

    def convert(self, event_to_convert):
        return self._convert_event(
            event_to_convert.copy(), core_parameters.DirectDuration(0)
        )


class FilterArcoNoteLike(core_converters.abc.SymmetricalEventConverter):
    def _convert_simple_event(self, event_to_convert, absolute_time):
        if (
            c := getattr(event_to_convert, "playing_indicator_collection", None)
        ) and c.string_contact_point.contact_point == "pizzicato":
            return core_events.SimpleEvent(event_to_convert.duration)
        return event_to_convert

    def convert(self, event_to_convert):
        return self._convert_event(
            event_to_convert.copy(), core_parameters.DirectDuration(0)
        )
