import os

from mutwo import project_converters

e2f0 = project_converters.EventToF0()


def f0(simultaneous_event, index):
    bpath = f"builds/f0/day_{index + 1}_voice_"
    for voice_index, event in enumerate(
        filter(
            lambda e: e.tag in ("tonic", "partner", "written_instable_pitch"),
            simultaneous_event,
        )
    ):
        dir_path = f"{bpath}{voice_index}"
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass
        path = f"{dir_path}/n.f0"
        with open(path, "w") as f:
            f.write(e2f0(event))
