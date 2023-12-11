"""Test entry that simply returns empty music with 0 duration."""

from mutwo import core_events
from mutwo import project_interfaces

seq, sim = core_events.TaggedSequentialEvent, core_events.TaggedSimultaneousEvent


def main(context, *args, **kwargs) -> project_interfaces.PEntryReturnType:
    return (
        sim([seq([], tag="b"), seq([], tag="v"), sim([], tag="r")]),
        project_interfaces.ResonatorTuple([]),
    )
