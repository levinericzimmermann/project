import functools
import itertools
import typing

from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities
from mutwo import music_events


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


def SimultaneousEvent_chordify(self) -> core_events.SequentialEvent:
    def slice_tuple_to_event(
        slice_tuple: tuple[core_events.abc.Event],
    ) -> music_events.NoteLike:
        flat_event_list = []
        for ev in slice_tuple:
            if isinstance(
                ev, (core_events.SequentialEvent, core_events.SimultaneousEvent)
            ):
                if ev:
                    # XXX: somehow some events have two children. I assume this
                    # is due to floating point errors (i'd expect them to only
                    # have one child). for now we just don't care about it and
                    # finger crossed everything goes well..
                    duration_tuple = tuple(c.duration for c in ev)
                    picked_child = ev[duration_tuple.index(max(duration_tuple))]
                    flat_event_list.append(picked_child)
            else:
                flat_event_list.append(ev)

        n = music_events.NoteLike(duration=slice_tuple[0].duration)
        for e in flat_event_list:
            try:
                pitch_list = e.pitch_list
            except AttributeError:
                continue
            n.pitch_list.extend(pitch_list)

        return n

    sim = core_events.SimultaneousEvent([_FronzenSequentialEvent(s[:]) for s in self])
    print("WITH FROZEN")
    return sim.sequentialize(slice_tuple_to_event)


def SimultaneousEvent_sequentialize(
    self, slice_tuple_to_event=None
) -> core_events.SequentialEvent:
    if slice_tuple_to_event is None:
        slice_tuple_to_event = core_events.SimultaneousEvent

    # Find all start/end times
    absolute_time_set = set([])
    for e in self:
        try:  # SequentialEvent
            (
                absolute_time_tuple,
                duration,
            ) = e._absolute_time_in_floats_tuple_and_duration
        except AttributeError:  # SimpleEvent or SimultaneousEvent
            absolute_time_tuple, duration = (0,), e.duration.duration_in_floats
        for t in absolute_time_tuple + (duration,):
            absolute_time_set.add(t)

    # Sort, but also remove the last entry: we don't need
    # to split at complete duration, because after duration
    # there isn't any event left in any child.
    absolute_time_list = sorted(absolute_time_set)[:-1]

    # Slice all child events
    slices = []
    for e in self:
        eslice_list = []
        previous_split_t = self.duration
        for split_t in reversed(absolute_time_list):
            print("s", split_t)
            if split_t == 0:  # We reached the end
                eslice = e
            else:
                try:
                    eslice = e.cut_out(split_t, previous_split_t, mutate=False)
                    e.cut_out(0, split_t)
                # Event is shorter etc.
                except core_utilities.InvalidStartAndEndValueError:
                    # We still need to append an event slice,
                    # because otherwise this slice group will be
                    # omitted (because we use 'zip').
                    eslice = None
            eslice_list.append(eslice)
            previous_split_t = split_t
        eslice_list.reverse()
        slices.append(eslice_list)

    # Finally, build new sequence from event slices
    sequential_event = core_events.SequentialEvent([])
    for slice_tuple in zip(*slices):
        if slice_tuple := tuple(filter(bool, slice_tuple)):
            e = slice_tuple_to_event(slice_tuple)
            sequential_event.append(e)

    return sequential_event


class _FronzenSequentialEvent(core_events.SequentialEvent):
    @functools.cached_property
    def _absolute_time_in_floats_tuple_and_duration(self):
        return super()._absolute_time_in_floats_tuple_and_duration

    @functools.cached_property
    def _absolute_time_tuple_and_duration(self):
        return super()._absolute_time_tuple_and_duration

    def copy(self):
        return _FronzenSequentialEvent(super().copy(self))


core_events.SimultaneousEvent.chordify = SimultaneousEvent_chordify
core_events.SimultaneousEvent.sequentialize = SimultaneousEvent_sequentialize


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
