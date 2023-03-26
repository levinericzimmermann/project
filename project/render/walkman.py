import warnings

import quicktions as fractions

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

    def is_rest(e):
        return not (hasattr(e, "pitch_list") and e.pitch_list)

    sequence_list = []
    for s in e:
        s.tie_by(lambda e0, e1: is_rest(e0) and is_rest(e1))
        sequence_list.append(mutwo2walkman(s))

    for start in range(0, 9, 3):
        s = e[start : start + 3].chordify()
        s.tie_by(lambda ev0, ev1: bool(ev0.pitch_list) == bool(ev1.pitch_list))
        for e0, e1 in zip(s, s[1:]):
            assert not (e0.pitch_list and e1.pitch_list), "tie by didn't work..."
            if e0.pitch_list:
                strong, weak = e0, e1
            else:
                strong, weak = e1, e0
            # try 7 seconds
            diff = min((weak.duration * fractions.Fraction(1, 2), 7))
            strong.duration += diff
            weak.duration -= diff
        sequence_list.append(mutwo2walkman(s, is_string=False))

    walkmanio.export(project.constants.WALKMAN_DATA_PATH, d, tuple(sequence_list))
