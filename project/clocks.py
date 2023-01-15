from quicktions import Fraction as f

import ranges

from mutwo import clock_converters
from mutwo import clock_events
from mutwo import clock_generators
from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_parameters

import project


# We may consider something like a
#
#   - 'silence_ratio'
#   - 'sound_ratio'
#
# which processes the sound/silence parts of a
# clock entry.


class ModalSymT(clock_generators.SymT):
    def __init__(self, duration_range=None):
        super().__init__("ModalEvent0", duration_range)


class ClockEndT(clock_generators.SymT):
    def __init__(self, duration_range=None):
        super().__init__("clock_end", duration_range)


# Non/Terminals
Tremolo1 = clock_generators.NT(
    project.entries.dynamic.tremolo_long,
    instrument_index_tuple=(1,),
    volume_tuple=("pp", "p"),
)
Tremolo2 = clock_generators.NT(
    project.entries.dynamic.tremolo_middle,
    instrument_index_tuple=(2,),
    tremolo_dynamic=music_parameters.Tremolo.D.Rit,
)

Grace = clock_generators.NT(project.entries.dynamic.grace)

Hit0 = clock_generators.NT(project.entries.dynamic.hit, instrument_index_tuple=(0,))
Hit2 = clock_generators.NT(project.entries.dynamic.hit, instrument_index_tuple=(2,))
Hit3 = clock_generators.NT(project.entries.dynamic.hit, instrument_index_tuple=(3,))
Hit4 = clock_generators.NT(project.entries.dynamic.hit, instrument_index_tuple=(4,))


R = clock_generators.R
context_free_grammar = clock_generators.ContextFreeGrammar(
    (
        # Symbolic
        R(ModalSymT(), (Hit4,), weight=1),
        R(ModalSymT(), (Tremolo1,), weight=1),
        R(ClockEndT(), (Hit0,), weight=1),
        # Real
        #   Modal Main
        R(Tremolo1, (Tremolo1, Tremolo2), weight=0.35),
        R(Tremolo1, (Tremolo1, Hit2), weight=1),
        R(Tremolo1, (Tremolo1, Grace), weight=1),
        R(Hit4, (Hit4, Tremolo2), weight=1),
        R(Hit4, (Hit4, Grace), weight=1),
        R(Grace, (Hit3, Hit2), weight=1),
        R(Grace, (Hit3, Hit2, Grace), weight=1),
        R(Hit2, (Hit2, Grace), weight=1),
        R(Hit2, (Hit2, Tremolo1), weight=0.5),
        R(Tremolo2, (Grace,), weight=1),
        #   Modal End
        R(Hit0, (Hit0, Tremolo2), weight=1),
    )
)


symt_sequence_to_clock_event_tuple = clock_converters.SymTSequenceToClockEventTuple(
    context_free_grammar
)


def apply_clock_events(
    modal_0_sequential_event: core_events.SequentialEvent[clock_events.ModalEvent0],
):
    filtered_seq = tuple(
        filter(
            lambda e: isinstance(e, clock_events.ModalEvent0), modal_0_sequential_event
        )
    )
    d = core_parameters.DirectDuration
    symt_list = []
    for modal_event_0 in filtered_seq:
        if getattr(modal_event_0, "is_end", False):
            symt = ClockEndT(
                duration_range=ranges.Range(d(f(10, 16)), d(f(30, 16))),
            )
        else:
            symt = ModalSymT(
                duration_range=ranges.Range(d(f(30, 16)), d(f(60, 16))),
            )
        symt_list.append(symt)
    clock_event_tuple = symt_sequence_to_clock_event_tuple.convert(
        symt_list, limit=LIMIT
    )
    for modal_event0, clock_event in zip(filtered_seq, clock_event_tuple):
        modal_event0.clock_event = clock_event
        # dummy event
        modal_event0.control_event = core_events.SequentialEvent(
            [core_events.SimpleEvent(1)]
        )


# Higher limit -> more options, but slower calculation
LIMIT = 5
