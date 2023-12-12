from mutwo import abjad_converters
from mutwo import core_events

import abjad

import project


def notate(event: core_events.SimultaneousEvent[core_events.TaggedSequentialEvent]):
    w2s = WhistleToStaff()
    r2s = ResonanceToStaff()

    whistle = w2s(event["v"])
    resonance = r2s(event["r"])

    score = abjad.Score([whistle, resonance])
    abjad.persist.as_pdf(score, f"builds/notations/{project.constants.TITLE}")


class SequentialEventToAbjadVoice(abjad_converters.SequentialEventToAbjadVoice):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            sequential_event_to_quantized_abjad_container=abjad_converters.LeafMakerSequentialEventToDurationLineBasedQuantizedAbjadContainer(),
            mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
            mutwo_volume_to_abjad_attachment_dynamic=None,
            tempo_envelope_to_abjad_attachment_tempo=None,
            duration_line_engraver=False,
            **kwargs,
        )

    def convert(self, *args, **kwargs):
        voice = super().convert(*args, **kwargs)
        leaf = abjad.get.leaf(voice, 0)
        abjad.attach(abjad.LilyPondLiteral(_voice_preperation), leaf)
        return voice


_voice_preperation = r"""
\omit Staff.BarLine
\omit Staff.TimeSignature
"""


class WhistleToStaff(SequentialEventToAbjadVoice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def convert(self, *args, **kwargs) -> abjad.Staff:
        voice = super().convert(*args, **kwargs)
        return abjad.Staff([voice])


class ResonanceToStaff(SequentialEventToAbjadVoice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def convert(self, *args, **kwargs) -> abjad.Staff:
        voice = super().convert(*args, **kwargs)
        leaf = abjad.get.leaf(voice, 0)
        abjad.attach(abjad.LilyPondLiteral(_resonance_preperation), leaf)
        return abjad.Staff([voice])

_resonance_preperation = r"""
\magnifyStaff #5/7
"""
