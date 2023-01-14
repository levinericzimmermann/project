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
    # r = note(context, min_duration=5, max_duration=10)
    r = note(context, min_duration=12, max_duration=17)
    return clock(context, event_list=[n, r])
