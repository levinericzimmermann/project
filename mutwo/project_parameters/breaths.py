import enum

from mutwo import core_parameters
from mutwo import project_parameters

__all__ = ("BreathDirection", "BreathSpeed", "Breath")


class BreathDirection(enum.Enum):
    INHALE = 0
    EXHALE = 1


class BreathSpeed(enum.Enum):
    SLOW = 0
    FAST = 1


class Breath(object):
    def __init__(
        self,
        direction: BreathDirection = BreathDirection.INHALE,
        speed: BreathSpeed = BreathSpeed.SLOW,
    ):
        self.direction = direction
        self.speed = speed

    @property
    def symbol(self) -> str:
        d, s = BreathDirection, BreathSpeed
        key = (self.direction, self.speed)
        match key:
            case (d.INHALE, s.SLOW):
                return "⇑"
            case (d.INHALE, s.FAST):
                return "↑"
            case (d.EXHALE, s.SLOW):
                return "⇓"
            case (d.EXHALE, s.FAST):
                return "↓"
            case _:
                raise NotImplementedError(key)

    @property
    def duration(self) -> core_parameters.abc.Duration:
        match self.speed:
            case BreathSpeed.SLOW:
                return core_parameters.DirectDuration(
                    project_parameters.constants.SLOW_BREATH_DURATION
                )
            case BreathSpeed.FAST:
                return core_parameters.DirectDuration(
                    project_parameters.constants.FAST_BREATH_DURATION
                )
            case _:
                raise NotImplementedError(self.speed)
