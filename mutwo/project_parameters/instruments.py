from mutwo import music_parameters
from mutwo import project_parameters

from mutwo.music_parameters.instruments.general import _setdefault


__all__ = ("Violin", "V", "InfinitePitchedInstrument")


class InfinitePitchedInstrument(music_parameters.ContinuousPitchedInstrument):
    """Simple fake instrument which can play any pitch in any octave

    Useful to be passed to algorithms which filter pitches based on instruments
    if one wants to filter later by its own.
    """

    def __init__(self, **kwargs):
        super().__init__(
            **_setdefault(
                kwargs,
                project_parameters.configurations.DEFAULT_INFINITE_PITCHED_INSTRUMENT_DICT,
            )
        )


class Violin(music_parameters.ContinuousPitchedStringInstrument):
    def __init__(self, **kwargs):
        super().__init__(
            **_setdefault(kwargs, project_parameters.configurations.DEFAULT_VIOLIN_DICT)
        )


# V can be both: a Viola or a Violoncello.
class V(music_parameters.ContinuousPitchedStringInstrument):
    def __init__(self, **kwargs):
        super().__init__(
            **_setdefault(kwargs, project_parameters.configurations.DEFAULT_V_DICT)
        )
