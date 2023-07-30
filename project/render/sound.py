import os
import shutil
import subprocess

from mutwo import project_converters


def sound(part_tuple, duration_tuple, path_tuple, people_tuple):
    c = project_converters.HarmonyTupleToSoundFileTuple()
    person_to_path_list = {p: [] for p in people_tuple}
    for i, d in enumerate(zip(part_tuple, duration_tuple, path_tuple)):
        part, duration, path = d
        person_to_path = c.convert(part, f"{i}_{path}", duration, people_tuple)
        for person in people_tuple:
            person_to_path_list[person].append(person_to_path[person])

    for person, sound_file_list in person_to_path_list.items():
        person_path = f"builds/sound/{person}"
        try:
            os.mkdir(person_path)
        except FileExistsError:
            pass
        for sf in sound_file_list:
            f = sf.split("/")[-1]
            shutil.copyfile(sf, f"{person_path}/{f}")
            subprocess.call(["zip", "-r", "builds/sound/{person}.zip", person_path])
