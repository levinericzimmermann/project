from quicktions import Fraction as f

from mutwo import clock_events
from mutwo import diary_interfaces
from mutwo import music_parameters


def is_supported(context=diary_interfaces.EmptyContext(), note=None, **kwargs):
    return note.is_supported(context, **kwargs)


def main(
    context=diary_interfaces.EmptyContext(),
    note=None,
    clock=None,
    min_duration=12,
    max_duration=20,
    min_rest_duration=4,
    max_rest_duration=8,
    tremolo_dynamic=music_parameters.Tremolo.D.AccRit,
    **kwargs,
):
    n = note(context, min_duration=min_duration, max_duration=max_duration, **kwargs)
    no = n.notation_indicator_collection
    no.duration_line.is_active = True
    pl = n.playing_indicator_collection
    pl.tremolo.flag_count = 32
    pl.tremolo.dynamic = tremolo_dynamic
    r = note(context, min_duration=min_rest_duration, max_duration=max_rest_duration)
    return clock(context, event_list=[n, r])
