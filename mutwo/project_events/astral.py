from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_parameters
from mutwo import project_parameters


__all__ = ("MoonPhaseEvent", "SunEvent", "MoonEvent")


class MoonPhaseEvent(core_events.SimpleEvent):
    def __init__(
        self,
        duration: core_parameters.abc.Duration,
        moon_phase: project_parameters.MoonPhase,
        intonation_tuple: tuple[music_parameters.JustIntonationPitch, ...] = tuple([]),
    ):
        self.moon_phase = moon_phase
        self.intonation_tuple = intonation_tuple
        super().__init__(duration)


class SunEvent(core_events.SimpleEvent):
    def __init__(
        self,
        duration: core_parameters.abc.Duration,
        sun_light: project_parameters.SunLight,
        pitch_tuple: tuple[music_parameters.JustIntonationPitch, ...] = tuple([]),
    ):
        self.sun_light = sun_light
        self.pitch_tuple = pitch_tuple
        super().__init__(duration)


class MoonEvent(core_events.SimpleEvent):
    def __init__(
        self,
        duration: core_parameters.abc.Duration,
        moon_light: project_parameters.MoonLight,
        pitch_tuple: tuple[music_parameters.JustIntonationPitch, ...] = tuple([]),
    ):
        self.moon_light = moon_light
        self.pitch_tuple = pitch_tuple
        super().__init__(duration)
