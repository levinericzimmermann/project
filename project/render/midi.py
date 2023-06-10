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


def midi(clock_tuple: tuple[clock_interfaces.Clock, ...]):
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

    grace_notes_converter = music_converters.GraceNotesConverter(
        minima_grace_notes_duration_factor=0.08, maxima_grace_notes_duration_factor=0.1
    )
    playing_indicators_converter = music_converters.PlayingIndicatorsConverter(
        (
            music_converters.TrillConverter(),
            music_converters.OptionalConverter(),
            music_converters.ArticulationConverter(),
            music_converters.StacattoConverter(),
            music_converters.ArpeggioConverter(duration_for_each_attack=0.3),
            project_converters.TremoloConverter(0.21, 1.25),
            project_converters.FlageoletConverter(),
            project_converters.BendAfterConverter(),
            project_converters.BridgeConverter(),
            project_converters.MovingOverpressureConverter(),
            project_converters.BowedBoxConverter(),
        )
    )

    event_to_midi_file = midi_converters.EventToMidiFile()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        task_list = []
        for event in simultaneous_event:
            event = grace_notes_converter(playing_indicators_converter(event))

            task_list.append(
                executor.submit(
                    event_to_midi_file.convert,
                    event,
                    f"builds/midi/{project.constants.TITLE}_{event.tag}.mid",
                )
            )

        done, not_done = concurrent.futures.wait(
            task_list, return_when=concurrent.futures.FIRST_EXCEPTION
        )
        for task in done:
            task.result()


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
