import concurrent.futures

import numpy as np
import ranges

from mutwo import clock_converters
from mutwo import clock_interfaces
from mutwo import core_events
from mutwo import core_parameters
from mutwo import midi_converters
from mutwo import music_converters
from mutwo import project_converters

import project


def midi(
    clock_tuple: tuple[clock_interfaces.Clock, ...],
    repetition_count_range: ranges.Range = ranges.Range(1, 3),
    random_seed: int = 100,
):
    clock2sim = clock_converters.ClockToSimultaneousEvent(
        project_converters.ClockLineToSimultaneousEvent()
    ).convert

    simultaneous_event = core_events.SimultaneousEvent([])
    for clock in clock_tuple:
        clock_simultaneous_event = clock2sim(
            clock, repetition_count=1
        )
        simultaneous_event.concatenate_by_tag(clock_simultaneous_event)

    adjust_tempo(simultaneous_event)

    grace_notes_converter = music_converters.GraceNotesConverter()
    playing_indicators_converter = music_converters.PlayingIndicatorsConverter(
        (
            music_converters.TrillConverter(),
            music_converters.OptionalConverter(),
            music_converters.ArticulationConverter(),
            music_converters.StacattoConverter(),
            music_converters.ArpeggioConverter(duration_for_each_attack=0.3),
            project_converters.TremoloConverter(0.21, 1.25),
        )
    )

    event_to_midi_file = midi_converters.EventToMidiFile()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for event in simultaneous_event:
            event = grace_notes_converter(playing_indicators_converter(event))
            executor.submit(
                event_to_midi_file.convert,
                event[0],
                f"builds/{project.constants.TITLE}_{event.tag}.mid",
            )


def adjust_tempo(simultaneous_event):
    tempo_main = 60
    tempo_envelope = core_events.TempoEnvelope(
        [
            [
                0,
                core_parameters.DirectTempoPoint(tempo_main),
            ],
            [
                simultaneous_event.duration,
                core_parameters.DirectTempoPoint(tempo_main),
            ],
        ]
    )
    simultaneous_event.set("tempo_envelope", tempo_envelope).metrize()
