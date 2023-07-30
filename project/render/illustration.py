import os
import subprocess

import abjad
import jinja2
import ranges

from mutwo import abjad_converters
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters


def illustration(part_tuple):
    base_path = "builds/illustrations"
    intro_tex_path = f"{base_path}/intro.tex"

    try:
        os.mkdir(base_path)
    except FileExistsError:
        pass

    part_notation_list = []
    for i, part in enumerate(part_tuple):
        harmony_tuple, _ = part
        p = f"{base_path}/harmony_{i}.png"
        illustrate_harmony_tuple(p, harmony_tuple)
        part_notation_list.append(p)

    illustrate_start(intro_tex_path, tuple(part_notation_list))


def illustrate_start(tex_path, part_notation_tuple):
    template = J2ENVIRONMENT.get_template("intro.tex.j2").render(
        part_notation_tuple=part_notation_tuple
    )
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def call_latex(tex_path: str):
    subprocess.call(["lualatex", "--output-directory=builds/illustrations/", tex_path])


J2ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader("etc/templates"))


def illustrate_harmony_tuple(
    path: str,
    harmony_tuple: tuple[tuple[music_parameters.JustIntonationPitch, ...], ...],
):
    def post_process_abjad_staff(abjad_staff):
        """post process abjad staff"""
        # This is actually not a good idea, because it's way to
        # noisy:
        #
        # leaf = abjad.get.leaf(abjad_staff, 0)
        # abjad.attach(abjad.LilyPondLiteral(r"\accidentalStyle dodecaphonic"), leaf)

    illustrate_snippet(
        path,
        core_events.SequentialEvent(
            [music_events.NoteLike(pitch_list=h, duration=1) for h in harmony_tuple]
        ),
        post_process_abjad_staff=post_process_abjad_staff,
        lilypond_file_preamble_tuple=(
            r'\include "etc/lilypond/ekme-heji.ily"',
            r'\include "lilypond-book-preamble.ly"',
            r"#(ly:set-option 'tall-page-formats 'png)",
        ),
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
    sequential_event_to_abjad_voice_kwargs={},
):
    sequential_event_to_abjad_voice_kwargs.setdefault(
        "mutwo_pitch_to_abjad_pitch", abjad_converters.MutwoPitchToHEJIAbjadPitch()
    )
    sequential_event_to_abjad_voice_kwargs.setdefault(
        "mutwo_volume_to_abjad_attachment_dynamic", None
    )
    sequential_event_to_abjad_voice_kwargs.setdefault(
        "tempo_envelope_to_abjad_attachment_tempo", None
    )
    seq2avoice = abjad_converters.SequentialEventToAbjadVoice(
        **sequential_event_to_abjad_voice_kwargs
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
