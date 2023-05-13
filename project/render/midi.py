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
        project_converters.ClockLineToSimultaneousEvent()
    ).convert

    simultaneous_event = core_events.SimultaneousEvent([])
    for clock in clock_tuple:
        clock_repetition_count = 1
        clock_simultaneous_event = clock2sim(
            clock, repetition_count=clock_repetition_count
        )
        simultaneous_event.concatenate_by_tag(clock_simultaneous_event)

    post_process_instruments(simultaneous_event)
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
            project_converters.ClusterConverter(project.constants.SCALE),
            project_converters.FlageoletConverter(),
            project_converters.BendAfterConverter(),
        )
    )

    event_to_midi_file = midi_converters.EventToMidiFile()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for event in simultaneous_event:
            event = grace_notes_converter(playing_indicators_converter(event))

            executor.submit(
                event_to_midi_file.convert,
                event,
                f"builds/midi/{project.constants.TITLE}_{event.tag}.mid",
            )


def post_process_instruments(simultaneous_event):
    filter_pizz = project_converters.FilterPizzicatoNoteLike()
    filter_arco = project_converters.FilterArcoNoteLike()

    event_to_remove_index_list = []
    event_to_add_list = []
    for event_index, event in enumerate(simultaneous_event):
        match event.tag:
            case project.constants.ORCHESTRATION.PCLOCK.name:
                event = project.constants.INSTRUMENT_CLOCK_EVENT_TO_PITCHED_CLOCK_EVENT(
                    event
                )
                event_to_remove_index_list.append(event_index)
                event_to_add_list.append(event)
            case project.constants.ORCHESTRATION.GLOCKENSPIEL.name:

                r = np.random.default_rng(10)

                def _(c):
                    # Can be played or can be not played
                    c.optional.is_active = True
                    # Can be bowed or can be hit
                    c.string_contact_point.contact_point = r.choice(
                        ["pizzicato", "arco"], p=[0.3, 0.7]
                    )

                event.mutate_parameter("playing_indicator_collection", _)

                event_to_remove_index_list.append(event_index)
                event_to_add_list.extend(
                    (
                        filter_pizz(
                            event.set("tag", f"{event.tag}_pizz", mutate=False)
                        ),
                        filter_arco(
                            event.set("tag", f"{event.tag}_arco", mutate=False)
                        ),
                    )
                )

            case project.constants.ORCHESTRATION.V.name:
                event_to_remove_index_list.append(event_index)
                event_to_add_list.extend(
                    (
                        filter_pizz(
                            event.set("tag", f"{event.tag}_pizz", mutate=False)
                        ),
                        filter_arco(
                            event.set("tag", f"{event.tag}_arco", mutate=False)
                        ),
                    )
                )

    for event_to_remove_index in reversed(event_to_remove_index_list):
        del simultaneous_event[event_to_remove_index]

    simultaneous_event.extend(event_to_add_list)


def adjust_tempo(simultaneous_event):
    import random

    random.seed(10)
    # SPEED UP. should later be slowed down again :)
    step = core_parameters.DirectDuration(10)
    index_count = int(simultaneous_event.duration / step) or 1

    tempo_main = 15 / 4
    # tempo_main = 30 / 4
    derivation = 3 / 4

    tempo_envelope = core_events.TempoEnvelope(
        [
            [
                step * index,
                core_parameters.DirectTempoPoint(random.gauss(tempo_main, derivation)),
            ]
            for index in range(index_count)
        ]
    )

    simultaneous_event.set("tempo_envelope", tempo_envelope).metrize()
