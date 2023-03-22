from mutwo import clock_converters
from mutwo import midi_converters
from mutwo import music_converters
from mutwo import project_converters

import project


def midi(simultaneous_event, executor):
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

    event_to_midi_file = midi_converters.EventToMidiFile(
        # distribute_midi_channels=True, midi_channel_count_per_track=1
    )

    future_list = []

    for event in simultaneous_event:
        event = grace_notes_converter(playing_indicators_converter(event))
        for s_index, seq in enumerate(event):
            future_list.append(executor.submit(
                event_to_midi_file.convert,
                seq,
                f"builds/{project.constants.TITLE}_{event.tag}_{s_index}.mid",
            ))
    return tuple(future_list)
