from mutwo import breath_parameters
from mutwo import core_events
from mutwo import music_events

import project


def is_supported(context, **kwargs):
    return True


def main(context, **kwargs):
    inh = core_events.SimpleEvent(project.constants.INTERNAL_BREATH_DURATION).set(
        "breath", breath_parameters.Breath(breath_parameters.BreathDirection.INHALE)
    )
    exh = core_events.SimpleEvent(project.constants.INTERNAL_BREATH_DURATION).set(
        "breath", breath_parameters.Breath(breath_parameters.BreathDirection.EXHALE)
    )
    n = music_events.NoteLike("7", 1)
    return core_events.SimultaneousEvent(
        [
            core_events.TaggedSequentialEvent([inh, exh, inh, exh] * 3, tag="b"),
            core_events.TaggedSequentialEvent([n] * 12, tag="v"),
            core_events.TaggedSequentialEvent([n] * 12, tag="i"),
        ]
    )
