from mutwo import breath_parameters
from mutwo import core_events
from mutwo import mmml_converters

import project


def parse_speed(speed):
    match speed:
        case "s":
            s = breath_parameters.BreathSpeed.SLOW
        case "f":
            s = breath_parameters.BreathSpeed.FAST
        case _:
            raise NotImplementedError(speed)
    return s


def b_event(breath):
    return core_events.SimpleEvent(project.constants.INTERNAL_BREATH_DURATION).set(
        "breath", breath
    )


@mmml_converters.register_decoder
def inh(speed="s"):
    return b_event(
        breath_parameters.Breath(
            breath_parameters.BreathDirection.INHALE, parse_speed(speed)
        )
    )


@mmml_converters.register_decoder
def exh(speed="s"):
    return b_event(
        breath_parameters.Breath(
            breath_parameters.BreathDirection.EXHALE, parse_speed(speed)
        )
    )
