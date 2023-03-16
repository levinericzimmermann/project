import itertools
import typing

from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities


# New features


@core_utilities.add_copy_option
def SequentialEvent_repeat(
    self,
    repetition_count: int,
    duration_factor_generator: typing.Generator = itertools.cycle((1,)),
) -> core_events.SequentialEvent:
    e, d = self[:], self.duration
    for _ in range(repetition_count):
        if (f := next(duration_factor_generator)) != 1:
            new_e = e.set("duration", d * f, mutate=False)
        else:
            new_e = e.copy()
        self.extend(new_e)


@core_utilities.add_copy_option
def SimultaneousEvent_repeat(
    self,
    repetition_count: int,
    duration_factor_generator: typing.Generator = itertools.cycle((1,)),
) -> core_events.SimultaneousEvent:
    for e in self:
        try:
            e.repeat(
                repetition_count, duration_factor_generator=duration_factor_generator
            )
        except AttributeError:
            raise


core_events.SequentialEvent.repeat = SequentialEvent_repeat
core_events.SimultaneousEvent.repeat = SimultaneousEvent_repeat


# Patches


@core_utilities.add_copy_option
def SequentialEvent_squash_in(
    self,
    start: core_parameters.abc.Duration | typing.Any,
    event_to_squash_in: core_events.abc.Event,
) -> core_events.SequentialEvent:
    start = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(start)
    start_in_floats = start.duration_in_floats

    self._assert_start_in_range(start_in_floats)

    # Only run cut_off if necessary -> Improve performance
    if (event_to_squash_in_duration := event_to_squash_in.duration) > 0:
        cut_off_end = start + event_to_squash_in_duration
        self._cut_off(start, cut_off_end, event_to_squash_in_duration)

    # We already know that the given start is within the
    # range of the event. This means that if the start
    # is bigger than the duration, it is only due to a
    # floating point rounding error. To avoid odd bugs
    # we therefore have to define the bigger-equal
    # relationship.
    (
        absolute_time_in_floats_tuple,
        duration_in_floats,
    ) = self._absolute_time_in_floats_tuple_and_duration
    if start_in_floats >= duration_in_floats:
        self.append(event_to_squash_in)
    else:
        try:
            insert_index = absolute_time_in_floats_tuple.index(start)
        # There is an event on the given point which need to be
        # split.
        except ValueError:
            active_event_index = (
                core_events.SequentialEvent._get_index_at_from_absolute_time_tuple(
                    start_in_floats,
                    absolute_time_in_floats_tuple,
                    duration_in_floats,
                )
            )
            split_position = (
                start_in_floats - absolute_time_in_floats_tuple[active_event_index]
            )
            if (
                split_position > 0
                and split_position < self[active_event_index].duration
            ):
                split_active_event = self[active_event_index].split_at(split_position)
                self[active_event_index] = split_active_event[1]
                self.insert(active_event_index, split_active_event[0])
                active_event_index += 1

            insert_index = active_event_index

        self.insert(insert_index, event_to_squash_in)


core_events.SequentialEvent.squash_in = SequentialEvent_squash_in
