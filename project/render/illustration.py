import os
import subprocess

import abjad
import jinja2
import ranges

from mutwo import abjad_converters
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters

import project


def illustration():
    base_path = "builds/illustrations"
    harp_scordatura_path = f"{base_path}/harp_tuning.png"
    glockenspiel_scordatura_path = f"{base_path}/glockenspiel_tuning.png"
    intro_tex_path = f"{base_path}/intro.tex"
    poem_path = f"{base_path}/poem.tex"

    try:
        os.mkdir(base_path)
    except FileExistsError:
        pass

    illustrate_poem(poem_path)
    illustrate_harp_tuning(project.constants.ORCHESTRATION, harp_scordatura_path)
    illustrate_glockenspiel_tuning(
        project.constants.ORCHESTRATION, glockenspiel_scordatura_path
    )
    illustrate_start(intro_tex_path, harp_scordatura_path, glockenspiel_scordatura_path)


def illustrate_harp_tuning(orchestration, path):
    pitch_range = ranges.Range(
        music_parameters.JustIntonationPitch("7/12"),
        music_parameters.JustIntonationPitch("7/6"),
    )
    pitch_tuple = tuple(p for p in orchestration.HARP.pitch_tuple if p in pitch_range)
    illustrate_tuning(path, pitch_tuple)


def illustrate_glockenspiel_tuning(orchestration, path):
    pitch_range = ranges.Range(
        music_parameters.JustIntonationPitch("7/3"),
        music_parameters.JustIntonationPitch("14/3"),
    )
    pitch_tuple = tuple(
        p for p in orchestration.GLOCKENSPIEL.pitch_tuple if p in pitch_range
    )
    illustrate_tuning(path, pitch_tuple, clef_name="treble^15")


def illustrate_tuning(path, pitch_tuple, clef_name=None, resolution=400, title=None):
    seq = core_events.SequentialEvent(
        [music_events.NoteLike(p, 1) for p in pitch_tuple]
    )
    if clef_name:
        seq[0].notation_indicator_collection.clef.name = clef_name
    for notelike in seq:
        c = round(
            notelike.pitch_list[0].cent_deviation_from_closest_western_pitch_class, 1
        )
        notelike.notation_indicator_collection.markup.content = (
            rf"\markup {{ \typewriter \teeny { c } }}"
        )
        notelike.notation_indicator_collection.markup.direction = abjad.enums.UP

    seq2avoice = abjad_converters.SequentialEventToAbjadVoice(
        mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
        mutwo_volume_to_abjad_attachment_dynamic=None,
        tempo_envelope_to_abjad_attachment_tempo=None,
    )
    abjad_staff = abjad.Staff([seq2avoice.convert(seq)])
    leaf_sequence = abjad.select.leaves(abjad_staff)
    first_leaf = leaf_sequence[0]
    abjad.attach(
        abjad.LilyPondLiteral(
            r"\omit Staff.BarLine "
            r"\omit Staff.TimeSignature "
            r'\accidentalStyle "dodecaphonic" '
        ),
        first_leaf,
    )
    abjad_score = abjad.Score([abjad_staff])
    lilypond_file = abjad.LilyPondFile()
    lilypond_file.items.append(
        "\n".join(
            (
                r'\include "etc/lilypond/ekme-heji.ily"',
                r'\include "lilypond-book-preamble.ly"',
                r"#(ly:set-option 'tall-page-formats 'png)",
            )
        )
    )
    if title:
        header = abjad.Block("header")
        header.items.append(
            r"title = \markup { \fontsize #-5 \medium \typewriter { "
            f'"{title}"'
            r" } }"
        )
        lilypond_file.items.append(header)
    lilypond_file.items.append(abjad_score)
    return abjad.persist.as_png(lilypond_file, path, resolution=resolution)


def illustrate_start(tex_path, harp_scordatura, glockenspiel_scordatura_path):
    template = J2ENVIRONMENT.get_template("intro.tex.j2").render(
        harp_scordatura=harp_scordatura,
        glockenspiel_scordatura=glockenspiel_scordatura_path,
    )
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def illustrate_poem(tex_path):
    template = J2ENVIRONMENT.get_template("poem.tex.j2").render(
        poem=project.constants.POEM.split("\n")
    )
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def call_latex(tex_path: str):
    subprocess.call(["lualatex", "--output-directory=builds/illustrations/", tex_path])


J2ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader("etc/templates"))
