import warnings

from mutwo import project_converters

import project
import walkmanio


def walkman(simultaneous_event, d):
    try:
        e = simultaneous_event["aeolian harp"]
    except KeyError:
        warnings.warn(f"No aeolian harp event found for {d}!")
        return

    mutwo2walkman = project_converters.SequentialEventToWalkmanEventTuple()

    sequence_list = []
    for s in e:
        sequence_list.append(mutwo2walkman(s))

    for start in range(0, 9, 3):
        s = e[start:start + 3].chordify()
        sequence_list.append(mutwo2walkman(s, is_string=False))

    walkmanio.export(project.constants.WALKMAN_DATA_PATH, d, tuple(sequence_list))
