"""Convert datetime to AstralEvent

AstralEvent contains information regarding the current daylight
situation + related moonlight and moonphase data.
"""

import datetime
import typing

from astral import sun, moon, LocationInfo, Depression
import ranges

from mutwo import clock_converters
from mutwo import clock_events
from mutwo import clock_interfaces
from mutwo import core_converters
from mutwo import core_events
from mutwo import diary_converters
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_parameters

__all__ = (
    "DatetimeToSimultaneousEvent",
    "DatetimeToSunLight",
    "DatetimeToMoonLight",
    "DatetimeToMoonPhase",
    "AstralEventToClockTuple",
    "AstralConstellationToOrchestration",
    "AstralConstellationToScale",
    "AstralEventToClockTuple",
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
        moonlight, d_moon_end = self._d_to_moon_light(d, d_end)
        add(moonlight, d, d_moon_end)
        while d_moon_end < d_end:
            moonlight, d_moon_new_end = self._d_to_moon_light(d_moon_end, d_end)
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
    def convert(self, d: datetime.datetime, d_end: datetime.datetime):
        try:
            mrise = moon.moonrise(self._location_info.observer, date=d)
        # Moon never raises on this date at this location
        except ValueError:
            mrise = d_end
        mset = moon.moonset(self._location_info.observer, date=d)
        d2 = d + datetime.timedelta(days=1)
        next_mset = moon.moonset(self._location_info.observer, date=d2)
        try:
            next_mrise = moon.moonrise(self._location_info.observer, date=d2)
        # Moon never raises on this date at this location
        except ValueError:
            next_mrise = d_end
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


class AstralConstellationToOrchestration(core_converters.abc.Converter):
    def __init__(
        self,
        moon_phase_to_intonation: dict,
        sun_light_to_pitch_index_tuple: dict,
        moon_light_to_pitch_index_tuple: dict,
    ):
        self._moon_phase_to_intonation = moon_phase_to_intonation
        self._sun_light_to_pitch_index_tuple = sun_light_to_pitch_index_tuple
        self._moon_light_to_pitch_index_tuple = moon_light_to_pitch_index_tuple

    def convert(
        self, sun_light, moon_phase, moon_light
    ) -> music_parameters.Orchestration:
        return music_parameters.Orchestration(
            AEOLIAN_HARP=project_parameters.AeolianHarp(
                self._moon_phase_to_intonation[moon_phase]
            )
        )


class AstralConstellationToScale(core_converters.abc.Converter):
    def __init__(
        self,
        moon_phase_to_intonation: dict,
        sun_light_to_pitch_index_tuple: dict,
        moon_light_to_pitch_index_tuple: dict,
    ):
        self._moon_phase_to_intonation = moon_phase_to_intonation
        self._sun_light_to_pitch_index_tuple = sun_light_to_pitch_index_tuple
        self._moon_light_to_pitch_index_tuple = moon_light_to_pitch_index_tuple

    def convert(self, sun_light, moon_phase, moon_light) -> music_parameters.Scale:
        intonation = self._moon_phase_to_intonation[moon_phase]
        pitch_list = [
            intonation[i] for i in self._sun_light_to_pitch_index_tuple[sun_light]
        ]
        main_pitch = intonation[self._moon_light_to_pitch_index_tuple[moon_light][0]]
        interval_list = sorted([(p - main_pitch).normalize() for p in pitch_list])
        return music_parameters.Scale(
            main_pitch, music_parameters.RepeatingScaleFamily(interval_list)
        )


class AstralEventToClockTuple(core_converters.abc.Converter):
    def __init__(
        self,
        astral_constellation_to_orchestration: AstralConstellationToOrchestration,
        astral_constellation_to_scale: AstralConstellationToScale,
    ):
        self._astral_constellation_to_orchestration = (
            astral_constellation_to_orchestration
        )
        self._astral_constellation_to_scale = astral_constellation_to_scale

    def convert(
        self,
        astral_event: core_events.SimultaneousEvent[core_events.TaggedSequentialEvent],
    ) -> tuple[clock_interfaces.Clock, ...]:
        # Sunlight: Which subconverter do we use?
        #   (also which context, is it modal or stochastic?)
        #
        # Moonlight: Each moonlight event == one clock
        #   So if there is (ABSENT, PRESENT, ABSENT) we have three clocks.
        #   If there is (ABSENT,) we only have one clock.
        #
        # Moon phase: Simply describes which intonations we use.
        #   Maybe also relevant for global parameter settings (for
        #   creating a form).
        clock_list = []
        for absolute_time, moon_phase_event in zip(
            astral_event["moon_phase"].absolute_time_tuple, astral_event["moon_phase"]
        ):
            astral_constellation = {
                a: astral_event[a].get_event_at(absolute_time).get_parameter(a)
                for a in "moon_phase sun_light moon_light".split(" ")
            }
            scale = self._astral_constellation_to_scale(**astral_constellation)
            orchestration = self._astral_constellation_to_orchestration(
                **astral_constellation
            )
            clock_count = len(astral_event["moon_light"])
            duration = moon_phase_event.duration
            # XXX: fast POC, improve ASAP
            # => for now we only have one algorithm to create a clock.
            # => but actually the algorithm MUST change depending on the
            #    sun light.
            clock_list.append(
                self._make_clock(orchestration, clock_count, scale, duration)
            )
        return tuple(clock_list)

    def _make_clock(
        self,
        orchestration: music_parameters.Orchestration,
        clock_count: int,
        scale: music_parameters.Scale,
        duration,
    ) -> clock_interfaces.Clock:
        duration = duration.duration

        # So we have a 60 seconds grid. Each interpolation
        # takes 60 seconds. This is slow and ok.
        scale_position_duration = 60  # seconds
        scale_position_count = int(duration // scale_position_duration)
        scale_position_duration = duration / scale_position_count

        clock_event = clock_events.ClockEvent(
            [
                core_events.SequentialEvent(
                    [
                        music_events.NoteLike(
                            pitch_list="c", duration=scale_position_duration
                        )
                    ]
                )
            ]
        )

        scale_position_list = []
        for i in range(scale_position_count):
            if i % 2 == 0:
                scale_position_list.append((0, 0))
            else:
                scale_position_list.append((2, 0))

        root_pitch_tuple = tuple(
            scale.scale_position_to_pitch(scale_position)
            for scale_position in scale_position_list
        )
        modal_sequential_event = core_events.SequentialEvent(
            [
                clock_events.ModalEvent0(
                    start_pitch,
                    end_pitch,
                    scale,
                    clock_event=clock_event,
                    control_event=clock_event,
                )
                for start_pitch, end_pitch in zip(
                    root_pitch_tuple, root_pitch_tuple[1:]
                )
            ]
        )

        modal_0_sequential_event_to_clock_line = clock_converters.Modal0SequentialEventToClockLine(
            (
                diary_converters.Modal0SequentialEventToEventPlacementTuple(
                    orchestration,
                    # Turn off modal1 mode converter for better performance
                    # (this is very expensive and we don't want to use any
                    #  modal1 context based entries here anyway).
                    add_mod1=False,
                ),
            )
        )
        main_clock_line = modal_0_sequential_event_to_clock_line.convert(
            modal_sequential_event
        )

        clock = clock_interfaces.Clock(main_clock_line)
        return clock
