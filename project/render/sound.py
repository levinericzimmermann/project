from mutwo import project_converters

def sound(part_tuple):
    c = project_converters.HarmonyTupleToSoundFileTuple()
    c.convert(part_tuple[0], '1')
