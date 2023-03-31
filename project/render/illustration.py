import subprocess

import abjad

from mutwo import abjad_converters
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters

import project


def illustrate_guitar_tuning(orchestration, d, path, executor):
    try:
        guitar = orchestration.GUITAR
    except AttributeError:
        return

    seq = core_events.SequentialEvent(
        [music_events.NoteLike(string.tuning, 1) for string in guitar.string_tuple]
    )
    seq[0].notation_indicator_collection.clef.name = "G_8"
    for notelike in seq:
        c = round(
            notelike.pitch_list[0].cent_deviation_from_closest_western_pitch_class, 2
        )
        notelike.notation_indicator_collection.markup.content = (
            rf"\markup {{ \typewriter \tiny { c } }}"
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
    header = abjad.Block("header")
    header.items.append(
        r"title = \markup { \fontsize #-5 \medium \typewriter { "
        f'"guitar tuning {d.year}/{d.month}/{d.day}"'
        r" } }"
    )
    lilypond_file.items.append(header)
    lilypond_file.items.append(abjad_score)
    return executor.submit(
        abjad.persist.as_png,
        lilypond_file,
        path,
        resolution=400,
    )


def illustrate_aeolian_harp_tuning(d, orchestration):
    return _get_aeolian_harp_tuning(d, orchestration)


def _get_aeolian_harp_tuning(d, orchestration):
    aeolian_harp = orchestration.AEOLIAN_HARP
    tuning = []
    for box_index, string_tuple in enumerate(aeolian_harp.string_tuple_for_each_box):
        tuning_part = []
        for string in string_tuple:
            p = string.tuning
            pname = p.get_closest_pythagorean_pitch_name()
            dev = round(p.cent_deviation_from_closest_western_pitch_class, 2)
            ratio = (p + music_parameters.JustIntonationPitch("2/1")).ratio
            pitch_data = f"{pname} ({ratio}): {dev}"
            tuning_part.append(pitch_data)
        tuning_part = ", ".join(tuning_part)
        tuning_part = rf"{{ \large box{box_index + 1} }} [{tuning_part}]"
        tuning.append(tuning_part)
    tuning = "\n\n".join(tuning)
    day = rf"{{\large {d.year}/{d.month}/{d.day} }}"
    separator = r"\vspace{0.5cm}"
    tuning = f"{day}\n\n{separator}\n{tuning}"
    return tuning


def merge_guitar_tuning(guitar_tuning_path_list):
    print(f"Concatenate '{guitar_tuning_path_list}'.")
    tex_path = "builds/guitar_tuning.tex"
    template = project.constants.J2ENVIRONMENT.get_template(
        "guitar_tuning.tex.j2"
    ).render(data=guitar_tuning_path_list)
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def merge_aeolian_harp_tuning(aeolian_harp_tuning_list):
    tex_path = "builds/aeolian_harp_tuning.tex"
    template = project.constants.J2ENVIRONMENT.get_template(
        "aeolian_harp_tuning.tex.j2"
    ).render(data=aeolian_harp_tuning_list)
    with open(tex_path, "w") as b:
        b.write(template)
    call_latex(tex_path)


def call_latex(tex_path: str):
    subprocess.call(["lualatex", "--output-directory=builds/", tex_path])
