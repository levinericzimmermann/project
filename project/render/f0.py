import os

from mutwo import core_events
from mutwo import project_converters

e2f0 = project_converters.EventToF0()


def f0(simultaneous_event, index):
    f_simultaneous_event = core_events.SimultaneousEvent(
        filter(
            lambda e: e.tag in ("tonic", "partner", "written_instable_pitch"),
            simultaneous_event,
        )
    )

    if index not in (0, 6):
        assert len(f_simultaneous_event) == VOICE_COUNT

    if not f_simultaneous_event:
        return

    dclock = distribute_clock(simultaneous_event)

    bpath = f"builds/f0/day_{index + 1}_voice_"

    for voice_index, event in enumerate(f_simultaneous_event):
        dir_path = f"{bpath}{voice_index}"
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass
        n_path = f"{dir_path}/n.f0"
        p_path = f"{dir_path}/p.f0"
        for p, e in ((n_path, event), (p_path, dclock[voice_index])):
            with open(p, "w") as f:
                f.write(e2f0(e.tie_by(lambda e0, e1: is_rest(e1), mutate=False)))


# The rhythmic orientation ('metronome') is distributed on 3 different arduino.
# Each arduino therefore doesn't only give pitch/intonation orientation, but
# also rhythmic orientation.
def distribute_clock(simultaneous_event):
    dclock = core_events.SimultaneousEvent(
        [core_events.SequentialEvent([]) for _ in range(VOICE_COUNT)]
    )
    for i, e in enumerate(
        simultaneous_event["pclock"][0].tie_by(lambda e0, e1: is_rest(e1))
    ):
        add_index = i % VOICE_COUNT
        for i2, seq in enumerate(dclock):
            if i2 == add_index:
                seq.append(e)
            else:
                seq.append(core_events.SimpleEvent(e.duration))
    return dclock


def is_rest(e):
    return not getattr(e, "pitch_list", [])


VOICE_COUNT = 3
