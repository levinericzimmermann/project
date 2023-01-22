#! /usr/bin/env nix-shell
#! nix-shell -i python --pure ./shell.nix

import concurrent.futures

import abjad
import jinja2
import subprocess

from mutwo import abjad_converters
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_events

import project


def book_of_moon_cycle() -> tuple[project_events.MoonPhaseEvent, ...]:
    return tuple(
        project_events.MoonPhaseEvent(1, moon_phase, intonation_tuple)
        for moon_phase, intonation_tuple in project.constants.MOON_PHASE_TO_INTONATION.items()
    )


def book_of_sun() -> tuple[project_events.SunEvent, ...]:
    return tuple(
        project_events.SunEvent(1, sun_light, pitch_tuple)
        for sun_light, pitch_tuple in project.constants.SUN_LIGHT_TO_PITCH_TUPLE.items()
    )


def book_of_moon() -> tuple[project_events.SunEvent, ...]:
    return tuple(
        project_events.MoonEvent(1, moon_light, pitch_tuple)
        for moon_light, pitch_tuple in project.constants.MOON_LIGHT_TO_PITCH_TUPLE.items()
    )


def notate_book_of_moon_cycle():
    """Create PDF: book of the lunar cycle"""
    moon_phase_event_tuple = book_of_moon_cycle()
    data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e:
        for i, moon_phase_event in enumerate(moon_phase_event_tuple):
            intonation_notation_path = f"builds/lunar_phase_intonation_{i}"
            e.submit(
                notate_intonation_tuple,
                moon_phase_event.intonation_tuple,
                intonation_notation_path,
            )
            data.append((moon_phase_event.moon_phase.name, intonation_notation_path))
    tex_path = "builds/book_of_moon_cycle.tex"
    template = J2ENVIRONMENT.get_template("book_of_moon_cycle.tex.j2").render(data=data)
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def notate_book_of_sun():
    """Create PDF: book of the sun"""
    sun_event_tuple = book_of_sun()
    data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e:
        for i, sun_event in enumerate(sun_event_tuple):
            path = f"builds/sun_light_{i}"
            e.submit(
                notate_pitch_tuple,
                sun_event.pitch_tuple,
                path,
            )
            data.append((sun_event.sun_light.name, path))
    template = J2ENVIRONMENT.get_template("book_of_sun.tex.j2").render(data=data)
    tex_path = "builds/book_of_sun.tex"
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def notate_book_of_moon():
    """Create PDF: book of the sun"""
    moon_event_tuple = book_of_moon()
    data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e:
        for i, moon_event in enumerate(moon_event_tuple):
            path = f"builds/moon_light_{i}"
            e.submit(
                notate_pitch_tuple,
                moon_event.pitch_tuple,
                path,
            )
            data.append((moon_event.moon_light.name, path))
    template = J2ENVIRONMENT.get_template("book_of_moon.tex.j2").render(data=data)
    tex_path = "builds/book_of_moon.tex"
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def notate_intonation_tuple(
    intonation_tuple: tuple[music_parameters.JustIntonationPitch, ...], path: str
):
    seq = core_events.SequentialEvent(
        [music_events.NoteLike(intonation, 1) for intonation in intonation_tuple]
    )
    notate_sequential_event(seq, path, accidental_style="dodecaphonic")


def notate_pitch_tuple(
    intonation_tuple: tuple[music_parameters.JustIntonationPitch, ...], path: str
):
    seq = core_events.SequentialEvent(
        [music_events.NoteLike(intonation, 1) for intonation in intonation_tuple]
    )
    notate_sequential_event(seq, path)


def notate_sequential_event(
    seq: core_events.SequentialEvent, path: str, accidental_style: str = "voice"
):
    sequential_event_to_abjad_voice = abjad_converters.SequentialEventToAbjadVoice(
        mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
        mutwo_volume_to_abjad_attachment_dynamic=None,
        tempo_envelope_to_abjad_attachment_tempo=None,
    )
    abjad_voice = sequential_event_to_abjad_voice(seq)
    first_leaf = abjad.select.leaves(abjad_voice)[0]
    abjad.attach(
        abjad.LilyPondLiteral(
            "\n".join(
                (
                    rf"\accidentalStyle {accidental_style}",
                    r"\omit Score.BarLine",
                    r"\omit Staff.TimeSignature",
                )
            )
        ),
        first_leaf,
    )
    abjad_score = abjad.Score([abjad.Staff([abjad_voice])])
    abjad_score_block = abjad.Block("score")
    abjad_score_block.items.append(abjad_score)
    lilypond_file = abjad.LilyPondFile()
    lilypond_file.items.extend(
        (
            r'\language "english"',
            r'\include "lilypond-book-preamble.ly"',
            r'\include "./etc/lilypond/ekme-heji.ily"',
            abjad_score_block,
        )
    )
    abjad.persist.as_png(lilypond_file, path, resolution=500)


def call_latex(tex_path: str):
    subprocess.call(["lualatex", "--output-directory=builds/", tex_path])


J2ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader("etc/templates"))


if __name__ == "__main__":
    # notate_book_of_moon_cycle()
    # notate_book_of_sun()
    notate_book_of_moon()
