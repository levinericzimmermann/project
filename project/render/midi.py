from mutwo import breath_converters
from mutwo import core_events
from mutwo import midi_converters
from mutwo import project_converters

import project


def midi():
    simultaneous_event = core_events.SimultaneousEvent([])
    breath_sequence_to_simultaneous_event = breath_converters.BreathSequenceToSimultaneousEvent()
    page_index_to_breath_sequence_tuple = (
        project_converters.PageIndexToBreathSequenceTuple()
    )
    for page_index in range(project.constants.PAGE_COUNT):
        for b in page_index_to_breath_sequence_tuple.convert(page_index):
            s = breath_sequence_to_simultaneous_event.convert(b)
            simultaneous_event.concatenate_by_tag(s)

    e2midi = midi_converters.EventToMidiFile()
    for ev in simultaneous_event:
        e2midi.convert(ev, f'builds/midi/{ev.tag}.mid')
