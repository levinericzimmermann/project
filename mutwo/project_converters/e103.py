import typing

from mutwo import core_converters
from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import project_events
from mutwo import project_generators

C103SequentialEvent: typing.TypeAlias = core_events.SequentialEvent[
    project_events.C103Event
]


class TonicMovementTupleToC103SequentialEvent(core_converters.abc.Converter):
    def convert(
        self, tonic_movement_tuple: tuple[music_parameters.JustIntonationPitch, ...]
    ) -> C103SequentialEvent:
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


class C103SequentialEventToContextTuple(core_converters.abc.Converter):
    def convert(self, sequential_event: C103SequentialEvent) -> tuple:
        def append():
            if previous is not None:
                end = e.duration + start
                context = diary_interfaces.H103Context(
                    start=previous_start, end=end, attr=attr, pitch=previous
                )
                context_list.append(context)

        context_list = []
        absolute_time_tuple = sequential_event.absolute_time_tuple

        for attr in ("tonic", "partner", "written_instable_pitch"):
            previous = None
            previous_start = None
            for start, e in zip(absolute_time_tuple, sequential_event):
                item = getattr(e.chord, attr)

                if item != previous:
                    append()
                    previous = item
                    previous_start = start

            append()

        return tuple(context_list)
