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
    v_scordatura_path = f"{base_path}/v_tuning.png"
    glockenspiel_scordatura_path = f"{base_path}/glockenspiel_tuning.png"
    perc0_path = f"{base_path}/perc0.png"
    perc1_path = f"{base_path}/perc1.png"
    perc2_path = f"{base_path}/perc2.png"
    intro_tex_path = f"{base_path}/intro.tex"
    poem_path = f"{base_path}/poem.tex"

    try:
        os.mkdir(base_path)
    except FileExistsError:
        pass

    illustrate_poem(poem_path)
    illustrate_harp_tuning(project.constants.ORCHESTRATION, harp_scordatura_path)
    illustrate_v_tuning(project.constants.ORCHESTRATION, v_scordatura_path)

    for p, perc_path in (
        (music_parameters.WesternPitch("b", 3), perc0_path),
        (music_parameters.WesternPitch("c", 4), perc1_path),
        (music_parameters.WesternPitch("d", 4), perc2_path),
    ):
        illustrate_percussion_instrument(perc_path, p)

    illustrate_glockenspiel_tuning(
        project.constants.ORCHESTRATION, glockenspiel_scordatura_path
    )
    illustrate_start(
        intro_tex_path,
        harp_scordatura_path,
        glockenspiel_scordatura_path,
        v_scordatura_path,
        perc0_path,
        perc1_path,
        perc2_path,
    )


def illustrate_harp_tuning(orchestration, path):
    pitch_range = ranges.Range(
        music_parameters.JustIntonationPitch("7/12"),
        music_parameters.JustIntonationPitch("7/6"),
    )
    pitch_tuple = tuple(p for p in orchestration.HARP.pitch_tuple if p in pitch_range)
    illustrate_tuning(path, pitch_tuple)


def illustrate_glockenspiel_tuning(orchestration, path):
    pitch_range = ranges.Range(
        music_parameters.JustIntonationPitch("1/2"),
        music_parameters.JustIntonationPitch("1/1"),
    )
    pitch_tuple = tuple(
        p for p in orchestration.GLOCKENSPIEL.pitch_tuple if p in pitch_range
    )
    illustrate_tuning(path, pitch_tuple, clef_name="treble")


def illustrate_v_tuning(orchestration, path):
    pitch_tuple = tuple(s.tuning for s in orchestration.V.string_tuple)
    illustrate_tuning(path, pitch_tuple, clef_name="bass")


def illustrate_tuning(path, pitch_tuple, clef_name=None, **kwargs):
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
    return illustrate_snippet(
        path,
        seq,
        post_process_first_abjad_leaf=lambda first_leaf: abjad.attach(
            abjad.LilyPondLiteral(
                r"\omit Staff.BarLine "
                r"\omit Staff.TimeSignature "
                r'\accidentalStyle "dodecaphonic" '
            ),
            first_leaf,
        ),
        lilypond_file_preamble_tuple=(
            r'\include "etc/lilypond/ekme-heji.ily"',
            r'\include "lilypond-book-preamble.ly"',
            r"#(ly:set-option 'tall-page-formats 'png)",
        ),
        **kwargs,
    )


def illustrate_percussion_instrument(path, pitch, **kwargs):
    seq = core_events.SequentialEvent([music_events.NoteLike(pitch, 1)])
    seq[0].notation_indicator_collection.clef.name = "percussion"
    return illustrate_snippet(
        path,
        seq,
        post_process_first_abjad_leaf=lambda first_leaf: abjad.attach(
            abjad.LilyPondLiteral(
                r"\omit Staff.BarLine "
                r"\omit Staff.TimeSignature "
                r"\override Staff.StaffSymbol.line-count = #1 "
                r"\override Staff.Dots.dot-count = #0 "
                r"\override Staff.NoteHead.duration-log = 2 "
            ),
            first_leaf,
        ),
        **kwargs,
    )


def illustrate_snippet(
    path,
    sequential_event,
    post_process_first_abjad_leaf=lambda first_leaf: abjad.attach(
        abjad.LilyPondLiteral(r"\omit Staff.BarLine " r"\omit Staff.TimeSignature "),
        first_leaf,
    ),
    post_process_abjad_staff=lambda _: _,
    lilypond_file_preamble_tuple=(
        r'\include "lilypond-book-preamble.ly"',
        r"#(ly:set-option 'tall-page-formats 'png)",
    ),
    clef_name=None,
    resolution=400,
    title=None,
):
    seq2avoice = abjad_converters.SequentialEventToAbjadVoice(
        mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
        mutwo_volume_to_abjad_attachment_dynamic=None,
        tempo_envelope_to_abjad_attachment_tempo=None,
    )
    abjad_staff = abjad.Staff([seq2avoice.convert(sequential_event)])
    post_process_abjad_staff(abjad_staff)
    leaf_sequence = abjad.select.leaves(abjad_staff)
    first_leaf = leaf_sequence[0]
    post_process_first_abjad_leaf(first_leaf)
    abjad_score = abjad.Score([abjad_staff])
    lilypond_file = abjad.LilyPondFile()
    lilypond_file.items.append("\n".join(lilypond_file_preamble_tuple))
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


def illustrate_start(
    tex_path,
    harp_scordatura,
    glockenspiel_scordatura_path,
    v_scordatura_path,
    perc0_path,
    perc1_path,
    perc2_path,
):
    template = J2ENVIRONMENT.get_template("intro.tex.j2").render(
        harp_scordatura=harp_scordatura,
        glockenspiel_scordatura=glockenspiel_scordatura_path,
        v_scordatura=v_scordatura_path,
        perc0_path=perc0_path,
        perc1_path=perc1_path,
        perc2_path=perc2_path,
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
