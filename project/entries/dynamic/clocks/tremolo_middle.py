from quicktions import Fraction as f

from mutwo import clock_events
from mutwo import diary_interfaces


def is_supported(context=diary_interfaces.EmptyContext(), tremolo=None, **kwargs):
    return tremolo.is_supported(context, **kwargs)


def main(
    context=diary_interfaces.EmptyContext(),
    tremolo=None,
    **kwargs,
):
    return tremolo(
        context,
        min_duration=6,
        max_duration=12,
        # min_rest_duration=4,
        min_rest_duration=12,
        # max_rest_duration=8,
        max_rest_duration=20,
        **kwargs,
    )
