from mutwo import clock_converters
from mutwo import clock_interfaces
from mutwo import core_events
from mutwo import core_parameters

import project

def sound(clock_tuple: tuple[clock_interfaces.Clock, ...]):
    clock2sim = clock_converters.ClockToSimultaneousEvent(
        clock_converters.ClockLineToSimultaneousEvent()
    ).convert

    simultaneous_event = core_events.SimultaneousEvent([])
    for clock in clock_tuple:
        clock_repetition_count = 1
        clock_simultaneous_event = clock2sim(
            clock, repetition_count=clock_repetition_count
        )
        simultaneous_event.concatenate_by_tag(clock_simultaneous_event)

    adjust_tempo(simultaneous_event)

    project.render.f0(simultaneous_event)
    project.render.midi(simultaneous_event)


def adjust_tempo(simultaneous_event):
    tempo_main = 14 / 4

    tempo_envelope = core_events.TempoEnvelope(
        [
            [
                d,
                core_parameters.DirectTempoPoint(tempo_main),
            ]
            for d in (0, simultaneous_event.duration)
        ]
    )

    simultaneous_event.set("tempo_envelope", tempo_envelope).metrize()
