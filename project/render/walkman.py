"""Create resonator data for walkman cues"""

import json

from mutwo import project_converters

import project


def walkman(data_tuple):
    data = {}
    for i, d in enumerate(data_tuple):
        _, resonator_tuple = d
        data[i] = r2s(resonator_tuple)

    jsondata = json.dumps(data)
    with open(f"builds/wm/{project.constants.TITLE}.json", "w") as f:
        f.write(jsondata)


r2s = project_converters.ResonatorTupleToSerializable()
