from mutwo import core_events
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert int(context.moon_phase_index) == 10
        assert hasattr(context.orchestration, "AEOLIAN_HARP")
    except AssertionError:
        return False
    return True


def main(context, **kwargs) -> timeline_interfaces.EventPlacement:
    aeolian_harp = context.orchestration.AEOLIAN_HARP
    sim = core_events.TaggedSimultaneousEvent(
        [core_events.SequentialEvent([core_events.SimpleEvent(1)]) for _ in range(9)],
        tag=aeolian_harp.name,
    )
    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([sim]),
        context.start,
        context.end,
    )
