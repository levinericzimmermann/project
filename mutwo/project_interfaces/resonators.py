import dataclasses

from mutwo import core_parameters
from mutwo import music_parameters

__all__ = ("ResonanceFilter", "Resonator", "ResonatorTuple")


@dataclasses.dataclass(frozen=True)
class ResonanceFilter(object):
    frequency: float = 440
    amplitude: float = 1
    decay: float = 0.5


@dataclasses.dataclass(frozen=True)
class Resonator(object):
    # 'delay' indicates the real duration in seconds,
    # so not the one-breath-duration, but the absolute
    # duration
    delay: core_parameters.abc.Duration = core_parameters.DirectDuration(0)

    # Harmonizer parameters
    pitch_factor_tuple: tuple[float, ...] = (1,)

    # Resonator parameters
    #   Which pitches when played create resonances
    resonating_pitch_tuple: tuple[music_parameters.abc.Pitch, ...] = (
        music_parameters.DirectPitch(440),
    )
    #   The individual filters the resonator is composed of.
    resonance_filter_tuple: tuple[ResonanceFilter, ...] = (ResonanceFilter(),)


class ResonatorTuple(tuple[Resonator, ...]):
    """All resonators that play during a given cue"""
