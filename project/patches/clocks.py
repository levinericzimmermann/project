import warnings

import abjad

from mutwo import clock_converters
from mutwo import clock_interfaces
from mutwo import clock_utilities
from mutwo import core_parameters
from mutwo import timeline_interfaces


# Fix: if there is no event placement for a tag
if 1:

    def _add_event_placements_to_abjad_score(
        self,
        clock_to_convert: clock_interfaces.Clock,
        tag_tuple,
        ordered_tag_tuple,
        abjad_score,
    ):
        event_placement_list: list[timeline_interfaces.EventPlacement] = []
        delay = core_parameters.DirectDuration(0)
        for clock_line in clock_to_convert.clock_line_tuple:
            if clock_line:
                clock_line_event_placement_tuple = (
                    self._timeline_to_event_placement_tuple.convert(
                        clock_line, tag_tuple
                    )
                )
                if delay > 0:
                    for event_placement in clock_line_event_placement_tuple:
                        event_placement.move_by(delay)
                event_placement_list.extend(clock_line_event_placement_tuple)
                delay += clock_line.duration

        tag_to_event_placement_tuple = (
            self._event_placement_tuple_to_split_event_placement_dict.convert(
                tuple(event_placement_list)
            )
        )

        ordered_tag_list = list(ordered_tag_tuple)
        for tag in tag_to_event_placement_tuple:
            if tag not in ordered_tag_list:
                ordered_tag_list.append(tag)

        clock_duration = clock_to_convert.duration
        for tag in ordered_tag_list:
            # ##############################################
            # ##############################################
            # ##############################################
            # START FIX
            try:
                event_placement_tuple = tag_to_event_placement_tuple[tag]
            except KeyError:
                continue
            # END FIX
            # ##############################################
            # ##############################################
            # ##############################################

            gapless_event_placement_tuple = (
                self._event_placement_tuple_to_gapless_event_placement_tuple.convert(
                    event_placement_tuple, clock_duration
                )
            )
            try:
                event_placement_to_abjad_staff_group = (
                    self._tag_to_abjad_staff_group_converter[tag]
                )
            except KeyError:
                warnings.warn(clock_utilities.UndefinedConverterForTagWarning(tag))
            else:
                abjad_container = abjad.Container([])
                for event_placement in gapless_event_placement_tuple:
                    abjad_staff_group = event_placement_to_abjad_staff_group.convert(
                        event_placement
                    )
                    abjad_container.append(abjad_staff_group)
                abjad_score.append(abjad_container)

    clock_converters.ClockToAbjadScore._add_event_placements_to_abjad_score = (
        _add_event_placements_to_abjad_score
    )
