import fractions
import typing

import abjad

from mutwo import abjad_converters
from mutwo import abjad_parameters
from mutwo import music_parameters


__all__ = (
    "Optional",
    "Tremolo",
    "DurationLine",
    "Cluster",
    "SonsXylo",
    "Flageolet",
    "RhythmicInformation",
)


class Optional(abjad_parameters.abc.BangEachAttachment):
    def process_leaf(self, leaf: abjad.Leaf):
        if isinstance(leaf, (abjad.Note, abjad.Chord)):
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\once \set fontSize = -2"
                    "\n"
                    r"\once \override ParenthesesItem.font-size = #1"
                    "\n"
                    r"\once \override ParenthesesItem.padding = #0.3"
                    "\n"
                    r"\parenthesize"
                ),
                leaf,
            )
        return leaf


LeafOrLeafSequence = abjad.Leaf | typing.Sequence[abjad.Leaf]


class Tremolo(abjad_parameters.abc.BangEachAttachment):
    def process_first_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        leaf = super().process_first_leaf(leaf)

        if self.indicator.dynamic is not None:
            return self._add_varying_tremolo(leaf)

        return leaf

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        if self.indicator.dynamic is None:
            abjad.attach(
                abjad.StemTremolo(
                    self.indicator.flag_count * (2**leaf.written_duration.flag_count)
                ),
                leaf,
            )
        return leaf

    def _add_varying_tremolo(self, leaf: abjad.Leaf):
        def acc(leaf):
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\override Beam.grow-direction = #RIGHT", site="absolute_before"
                ),
                leaf,
            )

        def rit(leaf):
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\override Beam.grow-direction = #LEFT", site="absolute_before"
                ),
                leaf,
            )

        match leaf:
            case abjad.Chord():

                def make_leaf(duration):
                    return abjad.Chord(leaf.written_pitches, duration)

            case abjad.Note():

                def make_leaf(duration):
                    return abjad.Note(leaf.written_pitch, duration)

            case _:
                raise NotImplementedError(leaf)

        new_leaf_duration = fractions.Fraction(1, 16)
        new_leaf_count = int(leaf.written_duration / new_leaf_duration)
        assert new_leaf_count > 2
        center = (new_leaf_count - 1) // 2
        leaf_sequence = abjad.Container(
            [make_leaf(new_leaf_duration) for _ in range(new_leaf_count)]
        )
        # https://lilypond.org/doc/v2.24/Documentation/notation/beams#feathered-beams
        # Don't add r"\featherDurations 2/1", this conflicts with scaleDurations
        # and it's not needed for the duration! It's only for midi output, which
        # we don't use from lilypond anyway.
        abjad.attach(abjad.StartBeam(), leaf_sequence[0])
        abjad.attach(abjad.StopBeam(), leaf_sequence[-1])
        D = music_parameters.Tremolo.D
        match self.indicator.dynamic:
            case D.Acc:
                acc(leaf_sequence[0])
            case D.Rit:
                rit(leaf_sequence[0])
            case D.AccRit:
                acc(leaf_sequence[0])
                rit(leaf_sequence[center])
                abjad.attach(abjad.StartBeam(), leaf_sequence[center])
                abjad.attach(abjad.StopBeam(), leaf_sequence[center])
            case D.RitAcc:
                rit(leaf_sequence[0])
                acc(leaf_sequence[center])
                abjad.attach(abjad.StartBeam(), leaf_sequence[center])
                abjad.attach(abjad.StopBeam(), leaf_sequence[center])
            case _:
                return leaf

        abjad.attach(
            abjad.LilyPondLiteral(
                r"\omit Staff.NoteHead \omit Staff.Stem", site="before"
            ),
            leaf_sequence[1],
        )

        abjad.attach(
            abjad.LilyPondLiteral(
                r"\override Beam.grow-direction = #'()"
                r"\undo \omit Staff.NoteHead \undo \omit Staff.Stem",
                site="after",
            ),
            leaf_sequence[-1],
        )

        difference = leaf.written_duration - (new_leaf_duration * new_leaf_count)
        assert difference >= 0
        rest_count = difference / new_leaf_duration
        assert int(rest_count) == rest_count
        for _ in range(int(rest_count)):
            leaf_sequence.append(abjad.Skip(new_leaf_duration))
        return leaf_sequence


abjad_parameters.Tremolo = Tremolo


class DurationLine(abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(abjad.LilyPondLiteral(r"\-", site="after"), leaf)
        return leaf


class Cluster(abjad_parameters.abc.BangEachAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        return abjad.Cluster([abjad.mutate.copy(leaf)])


class SonsXylo(abjad_parameters.abc.ToggleAttachment):
    def process_leaf(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> LeafOrLeafSequence:
        if self.indicator.activity:
            att = abjad.StartTextSpan(
                left_text=abjad.Markup(r'\typewriter {\tiny { "sons xylo." }}'),
                # style="solid-line-with-arrow",
            )
        else:
            att = abjad.StopTextSpan()

        abjad.attach(att, leaf)
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> tuple[abjad.Leaf, ...]:
        if previous_attachment is not None or self.indicator.is_active:
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)
        else:
            return leaf_tuple


class Flageolet(abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(abjad.LilyPondLiteral(r"\flageolet"), leaf)
        return leaf


class RhythmicInformation(abjad_parameters.abc.ToggleAttachment):
    def process_leaf(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> LeafOrLeafSequence:
        # If active, print rhythmic information, otherwise omit this.
        if self.indicator.activity:
            undo = r"\undo"
        else:
            undo = ""

        for attr in ("Staff.Stem", "Staff.Flag", "Staff.Beam"):
            abjad.attach(
                abjad.LilyPondLiteral(rf"{ undo } \omit { attr }"),
                leaf,
            )

        return leaf
