from mutwo import core_events
from mutwo import music_events


def SimultaneousEvent_chordify(self):
    return self.sequentialize(slice_tuple_to_event)


core_events.SimultaneousEvent.chordify = SimultaneousEvent_chordify


def slice_tuple_to_event(slice_tuple: tuple[core_events.abc.Event, ...]):
    e = music_events.NoteLike([], duration=slice_tuple[0].duration)
    for seq in slice_tuple:
        for n in seq:
            for p in n.pitch_list:
                if p not in e.pitch_list:
                    e.pitch_list.append(p)
    return e
