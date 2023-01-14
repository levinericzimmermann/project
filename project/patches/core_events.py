import itertools
import typing

from mutwo import core_events
from mutwo import core_utilities


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
