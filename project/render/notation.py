from mutwo import abjad_converters
from mutwo import core_events

import abjad

import project


def notate(data_tuple):
    event = _data_tuple_to_event(data_tuple)

    w2s = WhistleToStaff()
    r2s = ResonanceToStaff()

    whistle = w2s(event["v"])
    resonance = r2s(event["r"])

    score = abjad.Score([whistle, resonance])

    headerblock = abjad.Block('header')
    headerblock.items.append(header)

    scoreblock = abjad.Block("score")
    scoreblock.items.append(score)

    layoutblock = abjad.Block('layout')
    with open('etc/templates/layout.j2', 'r') as f:
        layoutblock.items.append(f.read())

    paperblock = abjad.Block('paper')
    with open('etc/templates/paper.j2', 'r') as f:
        paperblock.items.append(f.read())

    lilypond_file = abjad.LilyPondFile()

    lilypond_file.items.append(r'\include "etc/lilypond/ekme-heji.ily"')
    lilypond_file.items.append(headerblock)
    lilypond_file.items.append(layoutblock)
    lilypond_file.items.append(paperblock)
    lilypond_file.items.append(scoreblock)

    abjad.persist.as_pdf(lilypond_file, f"builds/notations/{project.constants.TITLE}")


def _data_tuple_to_event(data_tuple):
    event = core_events.SimultaneousEvent(
        [
            core_events.TaggedSequentialEvent([], tag="v"),
            core_events.TaggedSequentialEvent([], tag="r"),
        ]
    )

    for i, d in enumerate(data_tuple):
        e, *_ = d
        # Add electronic cue to notation
        pic = e["v"][0].playing_indicator_collection
        pic.cue.index = i + 1

        # Add breath symbols to notation
        for i, breath in enumerate(e["b"]):
            e["v"].get_event_at(
                i
            ).playing_indicator_collection.breath_indicator.breath = breath.breath_or_hold_breath

        # Extend to previous structure
        event["v"].extend(e["v"])
        event["r"].extend(e["r"].chordify())

    return event


header = rf'''
title = "11.1"
composer = "levin eric zimmermann"
tagline = ""
'''


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
