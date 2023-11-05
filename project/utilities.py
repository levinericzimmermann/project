from mutwo import mmml_converters

import project


# Syntactic sugar to parse strings into mutwo events
def m(arg: str, **kwargs):
    return _mml2e(arg, **kwargs)


_mml2e = mmml_converters.MMMLExpressionToEvent()


def page_index_to_current_melody_and_next_melody(page_index: int):
    note_counter = 0
    for i, subm in enumerate(project.constants.MELODY):
        for j, n in enumerate(subm):
            if note_counter == page_index:
                try:
                    nextm = project.constants.MELODY[i + 1]
                except IndexError:
                    nextm = project.constants.MELODY[0]
                return subm[j:], nextm
            note_counter += 1
    return project.constants.MELODY[0], project.constants.MELODY[1]
