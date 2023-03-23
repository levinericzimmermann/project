import abjad

from mutwo import abjad_converters
from mutwo import core_events
from mutwo import music_events


def illustration(orchestration, d, executor):
    return _illustrate_guitar_tuning(orchestration, d, executor)


def _illustrate_guitar_tuning(orchestration, d, executor):
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
            rf"\markup {{ \typewriter { c }ct }}"
        )
        notelike.notation_indicator_collection.markup.direction = "^"

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
        f"builds/guitar_tuning_{d.month}_{d.day}.png",
        resolution=400,
    )
