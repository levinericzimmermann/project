from mutwo import core_events
from mutwo import mmml_converters
from mutwo import project_events
from mutwo import project_parameters


def parse_speed(speed):
    match speed:
        case "s":
            s = project_parameters.BreathSpeed.SLOW
        case "f":
            s = project_parameters.BreathSpeed.FAST
        case _:
            raise NotImplementedError(speed)
    return s


def b_event(breath):
    return project_events.BreathEvent(breath)


@mmml_converters.register_decoder
def inh(speed="s"):
    return b_event(
        project_parameters.Breath(
            project_parameters.BreathDirection.INHALE, parse_speed(speed)
        )
    )


@mmml_converters.register_decoder
def exh(speed="s"):
    return b_event(
        project_parameters.Breath(
            project_parameters.BreathDirection.EXHALE, parse_speed(speed)
        )
    )


@mmml_converters.register_encoder(core_events.SimpleEvent)
def simple_event(s: core_events.SimpleEvent):
    breath = s.breath
    name = (
        "inh" if breath.direction == project_parameters.BreathDirection.INHALE else "exh"
    )
    speed = "s" if breath.speed == project_parameters.BreathSpeed.SLOW else "f"
    return f"{name} {speed}"
