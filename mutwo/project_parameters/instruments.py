from mutwo import music_parameters
from mutwo import project_parameters

from mutwo.music_parameters.instruments.general import _setdefault


__all__ = ("Violin",)


class Violin(music_parameters.ContinuousPitchedStringInstrument):
    def __init__(self, **kwargs):
        super().__init__(
            **_setdefault(kwargs, project_parameters.configurations.DEFAULT_VIOLIN_DICT)
        )
