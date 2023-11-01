"""testing breath API"""

from mutwo import breath_converters
from mutwo import breath_events
from mutwo import breath_parameters
from mutwo import core_events
from mutwo import midi_converters
from mutwo import music_events
from mutwo import music_parameters
from mutwo import kepathian_converters

pi = music_parameters.ScalePitch

d = [
    core_events.TaggedSequentialEvent(
        # [music_events.NoteLike(pi(0), 0.75), music_events.NoteLike(pi(1), 0.25)],
        [music_events.NoteLike(pi(0), 1)],
        tag="whistle",
    )
]

bt_in = breath_events.BreathTime(
    d,
    breath=breath_parameters.Breath(direction=breath_parameters.BreathDirection.INHALE),
)
bt_out = breath_events.BreathTime(
    d,
    breath=breath_parameters.Breath(direction=breath_parameters.BreathDirection.EXHALE),
)

breath_sequence = breath_events.BreathSequence(
    [bt_in, bt_out, bt_in, bt_out, bt_in, bt_out]
)

ktable = breath_converters.BreathSequenceToKTable().convert(breath_sequence)

content = kepathian_converters.KTableToSileStr().convert(ktable)
kepathian_converters.ContentToDocument().convert(content, "breath.pdf", cleanup=True)

sim = breath_converters.BreathSequenceToSimultaneousEvent().convert(breath_sequence)

midi_converters.EventToMidiFile().convert(sim, "breath.mid")
