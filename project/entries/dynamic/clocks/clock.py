from mutwo import clock_events
from mutwo import core_events
from mutwo import diary_interfaces


def is_supported(context=diary_interfaces.EmptyContext(), **kwargs):
    return True


def main(
    context=diary_interfaces.EmptyContext(),
    event_list=[],
    **kwargs,
):
    return clock_events.ClockEvent([core_events.SequentialEvent(event_list)])
