import typing

import abjad

from mutwo import abjad_converters
from mutwo import abjad_parameters


__all__ = ("Optional", "Tremolo", "DurationLine", "Cluster", "SonsXylo", "Flageolet")


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
        if (d := self.indicator.dynamic) is not None:
            abjad.attach(
                abjad.Markup(rf'\markup {{ "{d.value}" }}'), leaf, direction=abjad.UP
            )
        return leaf

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.StemTremolo(
                self.indicator.flag_count * (2**leaf.written_duration.flag_count)
            ),
            leaf,
        )
        return leaf


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
        abjad.attach(abjad.LilyPondLiteral(r'\flageolet'), leaf)
        return leaf
