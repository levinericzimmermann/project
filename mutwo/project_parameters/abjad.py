import typing

import abjad

from mutwo import abjad_converters
from mutwo import abjad_parameters


__all__ = ("Optional", "Tremolo", "DurationLine", "Cluster")


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
