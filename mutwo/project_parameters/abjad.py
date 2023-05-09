import fractions
import typing

import abjad

from mutwo import abjad_converters
from mutwo import abjad_parameters


__all__ = (
    "Optional",
    "Tremolo",
    "DurationLine",
    "Cluster",
    "SonsXylo",
    "Flageolet",
    "RhythmicInformation",
    "FlagStrokeStyle",
    "NoteHead",
)


class Optional(abjad_parameters.abc.BangEachAttachment):
    def process_leaf(self, leaf: abjad.Leaf):
        if isinstance(leaf, (abjad.Note, abjad.Chord)):
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\once \set fontSize = -2"
                    "\n"
                    r"\once \override NoteHead.Parentheses.font-size = 3"
                    "\n"
                    r"\parenthesize NoteHead",
                    site="absolute_before",
                ),
                leaf,
            )
        return leaf


LeafOrLeafSequence = abjad.Leaf | typing.Sequence[abjad.Leaf]


class Tremolo(abjad_parameters.abc.BangEachAttachment):
    leaf_maker = abjad.LeafMaker()

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
        leaf_sequence = abjad.Container([abjad.mutate.copy(leaf)])
        leaf_duration = fractions.Fraction(1, 8)
        line_length = int(leaf.written_duration / leaf_duration) * 2
        difference = leaf.written_duration - leaf_duration
        assert difference >= 0
        leaf_sequence[0].written_duration = leaf_duration
        if difference > 0:
            for leaf in self.leaf_maker(None, difference):
                leaf_sequence.append(abjad.Skip(leaf.written_duration))
        abjad.attach(
            abjad.LilyPondLiteral(
                rf"\{self.indicator.dynamic.name} #{line_length}", site="before"
            ),
            leaf_sequence[0],
        )
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

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment,
    ) -> tuple[abjad.Leaf, ...]:
        return (self.process_leaf(leaf_tuple[0], previous_attachment),) + leaf_tuple[1:]


class FlagStrokeStyle(abjad_parameters.abc.BangEachAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LilyPondLiteral(
                # Without autoBeamOff two 1/8 notes connect their beams and
                # we don't have any strikethroughs anymore.. therefore we also
                # need to turn auto beam off.
                rf'\autoBeamOff \once \override Flag.stroke-style = #"{self.indicator.style}"'
            ),
            leaf,
        )
        abjad.attach(abjad.LilyPondLiteral(r"\autoBeamOn", site="after"), leaf)
        return leaf


class NoteHead(abjad_parameters.abc.BangEachAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LilyPondLiteral(
                r"\once \override NoteHead.stencil = #ly:text-interface::print"
                "\n"
                r"\once \override NoteHead.text = \markup {"
                "\n\t"
                rf'\musicglyph #"{self.indicator.name}"'
                "\n"
                "}"
            ),
            leaf,
        )
        return leaf
