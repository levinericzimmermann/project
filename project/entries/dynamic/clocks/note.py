from quicktions import Fraction as f

from mutwo import clock_events
from mutwo import diary_interfaces
from mutwo import music_events

import project


def is_supported(context=diary_interfaces.EmptyContext(), **kwargs):
    return True


def main(
    context=diary_interfaces.EmptyContext(),
    random=None,
    instrument_index_tuple=[],
    volume_tuple="p pp mp".split(" "),
    min_duration=1,
    max_duration=2,
    **kwargs,
):
    o = project.constants.ORCHESTRATION_CLOCK
    instrument_list = [getattr(o, f"CLOCK_I{i}") for i in instrument_index_tuple]
    n_duration = int(random.integers(min_duration, max_duration))
    volume = random.choice(volume_tuple)
    n = music_events.NoteLike(
        instrument_list=instrument_list,
        duration=f(n_duration, 16),
        volume=volume,
    )
    return n
