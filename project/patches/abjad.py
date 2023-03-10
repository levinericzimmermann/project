import typing

import abjad

from mutwo import abjad_converters
from mutwo import abjad_parameters
from mutwo import core_utilities

# FIXES
if 1:

    # Without this fix, we only have the duration lines printed
    # for one of the harmonics for double harmonics.
    def NaturalHarmonicNodeList_detach_all_indicators(
        self, leaf_to_process: abjad.Chord
    ):
        for indicator in abjad.get.indicators(leaf_to_process):
            if not isinstance(indicator, abjad.LilyPondLiteral):
                abjad.detach(indicator, leaf_to_process)

    abjad_parameters.NaturalHarmonicNodeList._detach_all_indicators = (
        NaturalHarmonicNodeList_detach_all_indicators
    )

    # All indicators which don't replace leaf-by-leaf can
    # potentially break indicators which do replace leaf-by-leaf:
    # Because the second category expects leaf-only input, but the
    # first category may create outputs which break with this rule.

    def SequentialEventToAbjadVoice_apply_abjad_parameters_on_quantized_abjad_leaves(
        self,
        quanitisized_abjad_leaf_voice: abjad.Voice,
        related_abjad_leaf_index_tuple_tuple_per_simple_event: tuple[
            tuple[tuple[int, ...], ...], ...
        ],
        abjad_parameters_per_type_per_event_tuple: tuple[
            tuple[typing.Optional[abjad_parameters.abc.AbjadAttachment], ...], ...
        ],
    ) -> None:

        index_tuple_to_remove_list: list[tuple[int, ...]] = []

        # ############################################################# #
        # BEGIN MONKEY PATCH!                                           #
        # ############################################################# #
        def filter_key(abjad_parameters_per_type):
            abjad_parameters_per_type = tuple(filter(bool, abjad_parameters_per_type))
            if abjad_parameters_per_type:
                return int(abjad_parameters_per_type[0].replace_leaf_by_leaf is False)
            else:
                return 0

        abjad_parameters_per_type_per_event_tuple = sorted(
            abjad_parameters_per_type_per_event_tuple,
            key=filter_key,
        )
        # ############################################################# #
        # END MONKEY PATCH!                                             #
        # ############################################################# #

        for abjad_parameters_per_type in abjad_parameters_per_type_per_event_tuple:
            previous_attachment = None
            for related_abjad_leaf_index_tuple_tuple, attachment in zip(
                related_abjad_leaf_index_tuple_tuple_per_simple_event,
                abjad_parameters_per_type,
            ):
                if attachment and attachment.is_active:
                    index_tuple_to_remove_list.extend(
                        self._apply_abjad_attachment(
                            attachment,
                            previous_attachment,
                            quanitisized_abjad_leaf_voice,
                            related_abjad_leaf_index_tuple_tuple,
                        )
                    )
                    previous_attachment = attachment

        for index_tuple in reversed(index_tuple_to_remove_list):
            core_utilities.del_nested_item_from_index_sequence(
                index_tuple, quanitisized_abjad_leaf_voice
            )

    abjad_converters.SequentialEventToAbjadVoice._apply_abjad_parameters_on_quantized_abjad_leaves = (
        SequentialEventToAbjadVoice_apply_abjad_parameters_on_quantized_abjad_leaves
    )

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
