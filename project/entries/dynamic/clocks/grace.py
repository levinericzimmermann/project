from mutwo import clock_events
from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_events

import project

from quicktions import Fraction as f


def is_supported(context=diary_interfaces.EmptyContext(), note=None, **kwargs):
    return note.is_supported(context, **kwargs)


no = music_events.NoteLike


def main(
    context=diary_interfaces.EmptyContext(),
    random=None,
    note=None,
    clock=None,
    **kwargs
):
    o = project.constants.ORCHESTRATION_CLOCK
    instrument_index_tuple = (random.choice((2, 3)),)
    n = note(
        context,
        min_duration=2,
        max_duration=4,
        instrument_index_tuple=instrument_index_tuple,
        **kwargs
    )
    volume = n.volume
    n.grace_note_sequential_event = core_events.SequentialEvent(
        [
            no(
                instrument_list=[o.CLOCK_I3],
                duration=f(1, 4),
                volume=volume,
            ),
            no(
                instrument_list=[o.CLOCK_I2],
                duration=f(1, 4),
                volume=volume,
            ),
        ]
    )
    # r = note(context, min_duration=5, max_duration=12)
    r = note(context, min_duration=18, max_duration=22)
    return clock(context, event_list=[n, r])
