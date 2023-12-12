from mutwo import core_events
from mutwo import midi_converters


def midi(data_tuple):
    event = _data_tuple_to_event(data_tuple)
    e2m.convert(event['v'], "builds/midi/whistle.mid")
    e2m.convert(event['r'], "builds/midi/resonance.mid")


def _data_tuple_to_event(data_tuple):
    event = core_events.SimultaneousEvent(
        [
            core_events.TaggedSequentialEvent([], tag="v"),
            core_events.TaggedSimultaneousEvent([], tag="r"),
        ]
    )

    for i, d in enumerate(data_tuple):
        e, *_ = d

        vr = core_events.SimultaneousEvent([e['v'], e['r']])
        vr_split = vr.split_at(*tuple(range(int(float(vr.duration)))))

        assert len(vr_split) == len(e['b'])

        # Adjust duration to real duration that each breath takes
        for part, breath in zip(vr_split, e["b"]):
            part.duration = breath.duration
            event.concatenate_by_tag(part)

    return event


e2m = midi_converters.EventToMidiFile()
