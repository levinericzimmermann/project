"""Convert datetime to AstralEvent

AstralEvent contains information regarding the current daylight
situation + related moonlight and moonphase data.
"""

import datetime
import typing

from astral import sun, moon, LocationInfo, Depression
import ranges

from mutwo import core_converters
from mutwo import core_events
from mutwo import project_parameters

__all__ = (
    "DatetimeToSimultaneousEvent",
    "DatetimeToSunLight",
    "DatetimeToMoonLight",
    "DatetimeToMoonPhase",
)


class DatetimeConverter(core_converters.abc.Converter):
    def __init__(
        self, location_info: LocationInfo, dawn_dusk_depression=Depression.CIVIL
    ):
        self._location_info = location_info
        self._dawn_dusk_depression = dawn_dusk_depression


class DatetimeToSimultaneousEvent(DatetimeConverter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._d_to_sun_light = DatetimeToSunLight(*args, **kwargs)
        self._d_to_moon_light = DatetimeToMoonLight(*args, **kwargs)
        self._d_to_moon_phase = DatetimeToMoonPhase(*args, **kwargs)

    def convert(
        self, d: datetime.datetime
    ) -> core_events.SimultaneousEvent[core_events.TaggedSequentialEvent]:
        assert datetime.tzinfo, "Can't parse datetime without timezone!"
        sun_light, d_end = self._d_to_sun_light(d)
        timedelta = d_end - d
        dur = timedelta.total_seconds()
        tag, si = core_events.TaggedSequentialEvent, core_events.SimpleEvent
        sim = core_events.SimultaneousEvent(
            [
                tag(
                    [si(dur).set_parameter("sun_light", sun_light)],
                    tag="sun_light",
                ),
                self._make_moonlight_event(d, d_end, dur),
                tag(
                    [si(dur).set_parameter("moon_phase", self._d_to_moon_phase(d))],
                    tag="moon_phase",
                ),
            ]
        )
        return sim

    def _make_moonlight_event(
        self, d: datetime.datetime, d_end: datetime.datetime, dur: float
    ) -> core_events.TaggedSequentialEvent:
        def add(moonlight, start, end):
            dur = (end - start).total_seconds()
            moonlight_ev.append(
                core_events.SimpleEvent(dur).set_parameter("moon_light", moonlight)
            )

        moonlight_ev = core_events.TaggedSequentialEvent([], tag="moon_light")
        moonlight, d_moon_end = self._d_to_moon_light(d)
        add(moonlight, d, d_moon_end)
        while d_moon_end < d_end:
            moonlight, d_moon_new_end = self._d_to_moon_light(d_moon_end)
            add(moonlight, d_moon_end, d_moon_new_end)
            d_moon_end = d_moon_new_end
        return moonlight_ev.cut_out(0, dur)


class DatetimeToSunLight(DatetimeConverter):
    End: typing.TypeAlias = datetime.datetime

    def convert(self, d: datetime.datetime) -> tuple[project_parameters.SunLight, End]:
        """Return current sun light situation + datetime when situation ends

        :param d: Time when to search for sun light situation.
        """
        s = sun.sun(
            self._location_info.observer,
            date=d,
            dawn_dusk_depression=self._dawn_dusk_depression,
        )
        dawn, sunrise, sunset, dusk = (
            s[v] for v in "dawn sunrise sunset dusk".split(" ")
        )
        if d < dawn:  # Previous nightlight
            return project_parameters.SunLight.NIGHTLIGHT, dawn
        elif d >= dawn and d < sunrise:
            return project_parameters.SunLight.MORNING_TWILIGHT, sunrise
        elif d >= sunrise and d < sunset:
            return project_parameters.SunLight.DAYLIGHT, sunset
        elif d >= sunset and d < dusk:
            return project_parameters.SunLight.EVENING_TWILIGHT, dusk
        else:
            d2 = d + datetime.timedelta(days=1)
            dawn2 = sun.dawn(
                self._location_info.observer,
                date=d2,
            )
            return project_parameters.SunLight.NIGHTLIGHT, dawn2


class DatetimeToMoonLight(DatetimeConverter):
    def convert(self, d: datetime.datetime):
        mrise = moon.moonrise(self._location_info.observer, date=d)
        mset = moon.moonset(self._location_info.observer, date=d)
        d2 = d + datetime.timedelta(days=1)
        next_mrise = moon.moonrise(self._location_info.observer, date=d2)
        next_mset = moon.moonset(self._location_info.observer, date=d2)
        if mset > mrise:
            if d >= mrise and d < mset:
                return project_parameters.MoonLight.PRESENT, mset
            elif d >= mset and d < next_mrise:
                return project_parameters.MoonLight.ABSENT, next_mrise
            elif d < mrise:
                return project_parameters.MoonLight.ABSENT, mrise
            else:
                raise AssertionError(f"Current: {d}, mrise: {mrise}, mset: {mset}.")
        else:
            if d >= mset and d < mrise:
                return project_parameters.MoonLight.ABSENT, mrise
            elif d >= mrise and d < next_mset:
                return project_parameters.MoonLight.PRESENT, next_mset
            elif d < mset:
                return project_parameters.MoonLight.PRESENT, mset
            else:
                raise AssertionError(f"Current: {d}, mrise: {mrise}, mset: {mset}.")


class DatetimeToMoonPhase(DatetimeConverter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._datetime_to_moon_phase = ranges.RangeDict(
            {m.range: m for m in project_parameters.MoonPhase}
        )

    def convert(self, d: datetime.datetime):
        # "The moon phase does not depend on your location.
        # However what the moon actually looks like to you does depend on your location.
        # If you’re in the southern hemisphere it looks different than if you were in the northern hemisphere."
        # (reference: https://astral.readthedocs.io/en/latest/index.html?highlight=phase#phase)
        phase_index = moon.phase(d)
        return self._datetime_to_moon_phase[phase_index]
