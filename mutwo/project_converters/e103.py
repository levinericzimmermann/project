from mutwo import core_converters
from mutwo import core_events
from mutwo import music_parameters
from mutwo import project_events
from mutwo import project_generators


class TonicMovementTupleToC103SequentialEvent(core_converters.abc.Converter):
    def convert(
        self, tonic_movement_tuple: tuple[music_parameters.JustIntonationPitch, ...]
    ) -> core_events.SequentialEvent[project_events.C103Event]:
        seq = core_events.SequentialEvent([])
        for tonic in tonic_movement_tuple:
            chord_tuple = self._tonic_to_chord_tuple(tonic)
            for c in chord_tuple:
                seq.append(project_events.C103Event(c, 1))
        return seq

    def _tonic_to_chord_tuple(self, tonic):
        key = tonic.normalize(mutate=False).exponent_tuple
        try:
            chord_tuple = _tonic_to_130_chord_tuple[key]
        except KeyError:
            chord_tuple = _tonic_to_130_chord_tuple[
                key
            ] = project_generators.get_103_chord_tuple(tonic)
        return chord_tuple


_tonic_to_130_chord_tuple = {}
