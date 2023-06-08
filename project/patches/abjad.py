import abjad

from mutwo import abjad_converters
from mutwo import core_utilities

# FIXES
if 1:

    # We explicitly add \- via the DurationLine notation indicator! So the different to
    # upstream code is that we omit one '\-'!
    def _DurationLineBasedQuantizedAbjadContainerMixin_adjust_quantisized_abjad_leaves(
        self,
        quanitisized_abjad_leaf_voice: abjad.Container,
        related_abjad_leaves_per_simple_event: tuple[tuple[tuple[int, ...], ...], ...],
    ):
        is_first = True

        for abjad_leaves_indices in related_abjad_leaves_per_simple_event:
            if abjad_leaves_indices:
                first_element = core_utilities.get_nested_item_from_index_sequence(
                    abjad_leaves_indices[0], quanitisized_abjad_leaf_voice
                )
                if is_first:
                    self._prepare_first_element(first_element)
                    is_first = False

                is_active = bool(abjad.get.pitches(first_element))
                if is_active:
                    if len(abjad_leaves_indices) > 1:
                        abjad.detach(abjad.Tie(), first_element)

                    for indices in abjad_leaves_indices[1:]:
                        element = core_utilities.get_nested_item_from_index_sequence(
                            indices, quanitisized_abjad_leaf_voice
                        )
                        core_utilities.set_nested_item_from_index_sequence(
                            indices,
                            quanitisized_abjad_leaf_voice,
                            abjad.Skip(element.written_duration),
                        )

    abjad_converters.NauertSequentialEventToDurationLineBasedQuantizedAbjadContainer._adjust_quantisized_abjad_leaves = (
        _DurationLineBasedQuantizedAbjadContainerMixin_adjust_quantisized_abjad_leaves
    )
    abjad_converters.LeafMakerSequentialEventToDurationLineBasedQuantizedAbjadContainer._adjust_quantisized_abjad_leaves = (
        _DurationLineBasedQuantizedAbjadContainerMixin_adjust_quantisized_abjad_leaves
    )

