from quicktions import Fraction as f

from mutwo import clock_events
from mutwo import diary_interfaces


def is_supported(context=diary_interfaces.EmptyContext(), note=None, **kwargs):
    return note.is_supported(context, **kwargs)


def main(
    context=diary_interfaces.EmptyContext(),
    note=None,
    clock=None,
    **kwargs,
):
    n = note(context, min_duration=1, max_duration=3, **kwargs)
    return clock(context, event_list=[n])
