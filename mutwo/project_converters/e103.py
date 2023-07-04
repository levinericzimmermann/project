import itertools
import typing

import quicktions as fractions

from mutwo import common_generators
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import project_events
from mutwo import project_generators

C103SequentialEvent: typing.TypeAlias = core_events.SequentialEvent[
    project_events.C103Event
]


class TonicMovementTupleToC103SequentialEvent(core_converters.abc.Converter):
    def __init__(self):
        self._activity_level = common_generators.ActivityLevel()
        # self._chord_count_cycle = itertools.cycle((3, 4, 2, 4, 3))
        self._chord_count_cycle = itertools.cycle((3, 4, 5, 6, 5))
        self._rest_duration_cycle = itertools.cycle((100, 35, 70, 45))

    def convert(
        self, tonic_movement_tuple: tuple[music_parameters.JustIntonationPitch, ...]
    ) -> C103SequentialEvent:
        seq = core_events.SequentialEvent([])
        max_index = len(tonic_movement_tuple) - 1
        previous_chord = None
        for index, tonic in enumerate(tonic_movement_tuple):
            # Add tonal structures
            self._add_chords(tonic, index, seq, previous_chord)
            # Only add rest if this isn't the last event.
            if index != max_index:
                self._add_rest(seq)
            previous_chord = seq[-1].chord
        return seq

    def _add_chords(self, tonic, index, seq, previous_chord):
        """Add tonal content to SequentialEvent"""
        # Basic duration for a tonic is 'fractions.Fraction(200, 16)'.
        # But because there is a rest between each tonic, the real duration is
        # more something like 'fractions.Fraction(100, 16)'.
        # Then we make tonics longer which have main notes and we make tonics
        # shorter which have transition pitches.
        if index % 2 == 1:  # is_transition
            tonal_duration = fractions.Fraction(80, 16)
        else:
            tonal_duration = fractions.Fraction(120, 16)

        chord_tuple = self._tonic_to_chord_tuple(tonic)

        chord_count = next(self._chord_count_cycle)
        picked_chord_list = self._get_picked_chord_list(
            chord_tuple, chord_count, previous_chord
        )

        # Put chords into sequential event, distribute them evenly.
        for c, chord_duration in zip(
            picked_chord_list,
            common_generators.euclidean(tonal_duration.numerator, chord_count),
        ):
            if chord_duration > 0:
                c103event = project_events.C103Event(
                    c, fractions.Fraction(chord_duration, tonal_duration.denominator)
                )
                seq.append(c103event)

    def _get_picked_chord_list(self, chord_tuple, chord_count, previous_chord):
        """Find which chords to use for the current tonic ("orgelpunkt")."""

        # Can we make a connection to the previous chord?
        # Otherwise just take the first chord.
        first_chord = chord_tuple[0]
        if previous_chord is not None:
            first_chord = max(
                chord_tuple, key=lambda c: c.common_pitch_count(previous_chord)
            )

        # Okay and now the main algorithm starts: how do we connect
        # the last chord with new chords?
        #
        # There are multiple mechanisms in play:
        #
        #   1. Chords shouldn't reappear so often (equal distribution)
        #   2. We prefer smooth changes (e.g. sharing of tones)
        chord_counter = {chord: 0 for chord in chord_tuple}
        chord_counter[first_chord] = 1

        picked_chord_list = [first_chord]
        for _ in range(chord_count - 1):
            previous_chord = picked_chord_list[-1]

            allowed_chord_list = []
            for c in chord_tuple:
                if c == previous_chord:
                    continue
                common_count = c.common_pitch_count(previous_chord)
                if c.type != picked_chord_list[-1].type and common_count > 1:
                    allowed_chord_list.append(c)
                elif c.type == 0 and previous_chord.type == 0:
                    allowed_chord_list.append(c)

            picked_chord = min(allowed_chord_list, key=lambda c: chord_counter[c])
            chord_counter[picked_chord] += 1
            picked_chord_list.append(picked_chord)

        assert len(picked_chord_list) == chord_count

        return picked_chord_list

    def _add_rest(self, seq) -> bool:
        """Gives True if rest was added and otherwise False"""
        if self._activity_level(3):
            return False
        rest_duration = fractions.Fraction(next(self._rest_duration_cycle), 16)
        seq.append(project_events.C103Event(None, rest_duration))
        return True

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
        def append(start, end, previous, repetition_count, other_pitch_list):
            if previous is not None:
                context = diary_interfaces.H103Context(
                    start=start,
                    end=end,
                    attr=attr,
                    pitch=previous,
                    energy=repetition_count,
                    other_pitch_tuple=core_utilities.uniqify_sequence(
                        tuple(other_pitch_list)
                    ),
                )
                context_list.append(context)

        context_list = []
        absolute_time_tuple = sequential_event.absolute_time_tuple

        attr_tuple = ("tonic", "partner", "written_instable_pitch")
        for attr in attr_tuple:
            other_attr_tuple = tuple(a for a in attr_tuple if a != attr)
            previous = None
            previous_start = None
            previous_other_pitch_list = []
            repetition_count = 0
            for start, e in zip(absolute_time_tuple, sequential_event):
                if e.chord is not None:
                    item = getattr(e.chord, attr)
                    other_pitch_list = [getattr(e.chord, a) for a in other_attr_tuple]
                else:
                    item = None

                if item != previous:
                    append(
                        previous_start,
                        start,
                        previous,
                        repetition_count,
                        previous_other_pitch_list,
                    )
                    repetition_count = 0
                    previous = item
                    previous_start = start
                    previous_other_pitch_list = other_pitch_list

                repetition_count += 1

            append(
                previous_start,
                start + e.duration,
                previous,
                repetition_count,
                other_pitch_list,
            )

        for start, end, e in zip(
            absolute_time_tuple,
            absolute_time_tuple[1:] + (sequential_event.duration,),
            sequential_event,
        ):
            if e.chord:
                context_list.append(
                    diary_interfaces.H103Context(start=start, end=end, attr="pclock")
                )

        return tuple(context_list)
