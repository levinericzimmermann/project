from mutwo import core_events
from mutwo import project_parameters


class BreathEvent(core_events.SimpleEvent):
    def __init__(
        # Each breath is always represented with a duration of '1'
        self, breath_or_hold_breath: project_parameters.BreathOrHoldBreath, duration=1, **kwargs
    ):
        super().__init__(duration, **kwargs)
        self.breath_or_hold_breath = breath_or_hold_breath
