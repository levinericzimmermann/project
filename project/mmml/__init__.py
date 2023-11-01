from mutwo import breath_events
from mutwo import core_events
from mutwo import mmml_converters

import project


def parse(name: str):
    with open(name, "r") as f:
        mmml = f.read()
    event = mmml_converters.MMMLExpressionToEvent().convert(mmml)
    assert event.duration == (
        project.constants.BREATH_COUNT_PER_PAGE
        * project.constants.INTERNAL_BREATH_DURATION
    )

    split_position_tuple = tuple(
        n * project.constants.INTERNAL_BREATH_DURATION
        for n in range(1, project.constants.BREATH_COUNT_PER_PAGE)
    )
    split_events = {ev.tag: ev.split_at(*split_position_tuple) for ev in event}

    indices = tuple(
        range(
            0,
            project.constants.BREATH_COUNT_PER_PAGE + 1,
            project.constants.BREATH_COUNT_PER_LINE,
        )
    )
    breath_sequence_list = []
    for start, end in zip(indices, indices[1:]):
        breath_sequence = core_events.SequentialEvent([])
        for b, v, i in zip(*[split_events[tag][start:end] for tag in ("b", "v", "i")]):
            breath_time = breath_events.BreathTime(breath=b[0].breath)
            breath_time.append(core_events.TaggedSequentialEvent(v, tag="v"))
            breath_time.append(core_events.TaggedSequentialEvent(i, tag="i"))
            breath_sequence.append(breath_time)

        assert len(breath_sequence) == project.constants.BREATH_COUNT_PER_LINE

        breath_sequence_list.append(breath_sequence)

    assert len(breath_sequence_list) == project.constants.LINE_COUNT_PER_PAGE

    return breath_sequence_list
