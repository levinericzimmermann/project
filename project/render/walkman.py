import warnings

from mutwo import project_converters

import project
import walkmanio


def walkman(simultaneous_event, d):
    mutwo2walkman = project_converters.SequentialEventToWalkmanEventTuple()
    sequence_list = []
    try:
        for s in simultaneous_event["aeolian harp"]:
            sequence_list.append(mutwo2walkman(s))
    except KeyError:
        warnings.warn(f"No aeolian harp event found for {d}!")
        return
    walkmanio.export(project.constants.WALKMAN_DATA_PATH, d, tuple(sequence_list))
