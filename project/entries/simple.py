from mutwo import breath_parameters
from mutwo import core_events
from mutwo import music_events
from mutwo import project_converters

import project


def is_supported(context, **kwargs):
    return True


def main(context, **kwargs):
    b = project.u.m(b0)

    def data_to_wait_count(is_first_note, trial_counter, missed_change_counter):
        if is_first_note:
            return 0
        if trial_counter == 0:
            return 0
        return 1

    v = mb2v.convert(context.melody, b, data_to_wait_count)

    i = v.copy().set("tag", "i")
    for split in range(int(i.duration)):
        i.split_child_at(split + 0.5)
    for index, n in enumerate(i):
        if index % 2 == 1:
            n.pitch_list = []
    del i[0]
    i[-1].duration += 0.5

    return core_events.SimultaneousEvent([b, v, i])


mb2v = project_converters.MelodyAndBreathSequenceToVoice()


b0 = r"""
seq b
    inh s
    exh s
    inh s
    exh s

    inh s
    exh s
    inh s
    exh s

    inh s
    exh s
    inh s
    exh s
"""
