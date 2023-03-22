"""Convert datetime to AstralEvent

AstralEvent contains information regarding the current daylight
situation + related moonlight and moonphase data.
"""

import datetime
import itertools
import typing
import warnings

from astral import sun, moon, LocationInfo, Depression
import ranges

from mutwo import clock_converters
from mutwo import clock_events
from mutwo import clock_interfaces
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import diary_converters
from mutwo import diary_interfaces
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_converters
from mutwo import project_parameters
from mutwo import timeline_interfaces

__all__ = (
    "DatetimeToSimultaneousEvent",
    "DatetimeToSunLight",
    "DatetimeToMoonLight",
    "DatetimeToMoonPhase",
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
        moon_phase, moon_phase_index = self._d_to_moon_phase(d, sun_light)
        sim = core_events.SimultaneousEvent(
            [
                tag(
                    [si(dur).set_parameter("sun_light", sun_light)],
                    tag="sun_light",
                ),
                self._make_moonlight_event(d, d_end, dur),
                tag(
                    [
                        si(dur)
                        .set_parameter("moon_phase", moon_phase)
                        .set_parameter("moon_phase_index", moon_phase_index)
                    ],
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

    def convert(self, d: datetime.datetime, sun_light: project_parameters.SunLight):
        # We adjust the datetime to ensure that we have the same moon_phase
        # for all sun light parts of the given day.
        d = datetime.datetime(d.year, d.month, d.day, 0, 0, tzinfo=d.tzinfo)
        # But we also adjust a
        # delta of -1 for morning twilight and daylight, because I always
        # retune the instruments before I play (so before evening twilight),
        # therefore during the morning and during the moon the tuning must
        # still be the same as it was during the previous day.
        if sun_light in (
            project_parameters.SunLight.MORNING_TWILIGHT,
            project_parameters.SunLight.DAYLIGHT,
        ):
            d -= datetime.timedelta(days=1)
        # "The moon phase does not depend on your location.
        # However what the moon actually looks like to you
        # does depend on your location.
        # If you’re in the southern hemisphere it looks different
        # than if you were in the northern hemisphere."
        # (reference: https://astral.readthedocs.io/en/latest/index.html?highlight=phase#phase)
        phase_index = moon.phase(d)
        return self._datetime_to_moon_phase[phase_index], phase_index


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
        self, sun_light, moon_phase, moon_light, **kwargs
    ) -> music_parameters.Orchestration:
        return music_parameters.Orchestration(
            AEOLIAN_HARP=project_parameters.AeolianHarp(
                self._moon_phase_to_intonation[moon_phase]
            ),
            CLAVICHORD=self._make_clavichord(
                self._moon_phase_to_intonation[moon_phase]
            ),
        )

    def _make_clavichord(
        self, pitch_tuple: tuple[music_parameters.abc.Pitch, ...]
    ) -> music_parameters.DiscreetPitchedStringInstrument:
        pitch_tuple = music_parameters.Scale(
            music_parameters.JustIntonationPitch("1/1"),
            music_parameters.RepeatingScaleFamily(
                pitch_tuple,
                min_pitch_interval=music_parameters.JustIntonationPitch("5/24"),
                max_pitch_interval=music_parameters.JustIntonationPitch("6/1"),
            ),
        ).pitch_tuple
        string_tuple = tuple(
            music_parameters.String(i, p) for i, p in enumerate(pitch_tuple)
        )
        return project_parameters.Clavichord(
            pitch_tuple=pitch_tuple,
            string_tuple=string_tuple,
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

    def convert(
        self, sun_light, moon_phase, moon_light, **kwargs
    ) -> music_parameters.Scale:
        intonation = self._moon_phase_to_intonation[moon_phase]
        pitch_list = [
            intonation[i] for i in self._sun_light_to_pitch_index_tuple[sun_light]
        ]
        main_pitch = intonation[self._moon_light_to_pitch_index_tuple[moon_light][0]]
        interval_list = sorted([(p - main_pitch).normalize() for p in pitch_list])
        return music_parameters.Scale(
            main_pitch,
            music_parameters.RepeatingScaleFamily(
                interval_list,
                min_pitch_interval=music_parameters.JustIntonationPitch("1/8"),
                max_pitch_interval=music_parameters.JustIntonationPitch("8/1"),
            ),
        )


class AstralEventToClockTuple(core_converters.abc.Converter):
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

    def __init__(
        self,
        astral_constellation_to_orchestration: AstralConstellationToOrchestration,
        astral_constellation_to_scale: AstralConstellationToScale,
    ):
        self._astral_constellation_to_orchestration = (
            astral_constellation_to_orchestration
        )
        self._astral_constellation_to_scale = astral_constellation_to_scale
        self._context_tuple_to_event_placement_tuple = (
            diary_converters.ContextTupleToEventPlacementTuple()
        )

    def convert(
        self,
        astral_event: core_events.SimultaneousEvent[core_events.TaggedSequentialEvent],
    ) -> tuple[tuple[clock_interfaces.Clock, ...], music_parameters.Orchestration]:
        clock_list = []

        sun_light = astral_event["sun_light"].get_parameter("sun_light", flat=True)[0]

        for absolute_time, moon_light_event in zip(
            astral_event["moon_light"].absolute_time_tuple, astral_event["moon_light"]
        ):
            astral_constellation = {}
            for a in "moon_phase sun_light moon_light".split(" "):
                ev = astral_event[a].get_event_at(absolute_time)
                parameter_tuple: tuple[str, ...] = (a,)
                if a == "moon_phase":
                    parameter_tuple = (a, "moon_phase_index")
                for parameter in parameter_tuple:
                    astral_constellation[parameter] = ev.get_parameter(parameter)
            scale = self._astral_constellation_to_scale(**astral_constellation)
            orchestration = self._astral_constellation_to_orchestration(
                **astral_constellation
            )
            duration = moon_light_event.duration

            clock = None

            match sun_light:
                case project_parameters.SunLight.MORNING_TWILIGHT:
                    clock = self._make_clock_morning_twilight(
                        orchestration, scale, duration
                    )
                case project_parameters.SunLight.DAYLIGHT:
                    clock = self._make_clock_daylight(orchestration, scale, duration)
                case project_parameters.SunLight.EVENING_TWILIGHT:
                    clock = self._make_clock_evening_twilight(
                        orchestration, scale, duration
                    )
                case project_parameters.SunLight.NIGHTLIGHT:
                    clock = self._make_clock_nightlight(
                        orchestration,
                        scale,
                        duration,
                        astral_constellation["moon_phase_index"],
                    )

            if clock:
                clock_list.append(clock)
            else:
                warnings.warn(f"NO CLOCK CREATED FOR '{sun_light}'!")

        return tuple(clock_list), orchestration

    def _make_clock_morning_twilight(
        self,
        orchestration: music_parameters.Orchestration,
        scale: music_parameters.Scale,
        duration,
    ):
        return self._make_empty_clock(duration, orchestration)

    def _make_clock_daylight(
        self,
        orchestration: music_parameters.Orchestration,
        scale: music_parameters.Scale,
        duration,
    ):
        return self._make_empty_clock(duration, orchestration)

    def _make_clock_nightlight(
        self,
        orchestration: music_parameters.Orchestration,
        scale: music_parameters.Scale,
        duration,
        moon_phase_index,
    ):
        main_clock_line = self._make_empty_clock_line(duration)
        moon_context_tuple = (
            diary_interfaces.MoonContext(0, duration, orchestration, moon_phase_index),
        )
        event_placement_tuple = self._context_tuple_to_event_placement_tuple.convert(
            moon_context_tuple
        )
        for e in event_placement_tuple:
            main_clock_line.register(e)
        clock = clock_interfaces.Clock(main_clock_line)
        return clock

    def _make_clock_evening_twilight(
        self,
        orchestration: music_parameters.Orchestration,
        scale: music_parameters.Scale,
        duration,
    ) -> clock_interfaces.Clock:
        duration = duration.duration

        # XXX: faster render for tests
        # duration *= 0.5

        # We take exactly 4 durations, because a gatra consist
        # of 4 events. So the structure repeats after each gatra.
        # So one gatra/phrase takes around 4, 5 minutes (this
        # is a basic melodic phrase).
        default_pattern = (3, 6, 4, 7)
        odd_pattern = (3, 5, 3, 6, 2, 4, 2, 4, 2, 2, 3, 4, 3, 5, 4, 6)
        # ev_duration_cycle = itertools.cycle(([odd_pattern] * 5))
        ev_duration_cycle = itertools.cycle((default_pattern * 2) + odd_pattern)

        # If the tempo is faster, there is less space
        # and the likelihood that clavichord and aeolian
        # harp are overlapping is higher.
        avg_t = 3.7  # XXX: Tempo > 3.75 breaks the notation, Idk why,
        #  but we can simply vary bar size instead of tempo.
        # tempo_cycle = itertools.cycle(([avg_t] * 7) + [8, 7])
        tempo_cycle = itertools.cycle(([avg_t] * 7))

        clock_event_list = []
        clock_duration = 0
        while clock_duration < duration:
            ev_duration = next(ev_duration_cycle)

            # If we use a higher tempo the score is longer and more verbose.
            # With a too low tempo the score is too dense / almost unreadable.
            tempo = core_parameters.DirectTempoPoint(
                next(tempo_cycle)
            )  # 4/1 == 60 seconds

            # We add the tempo straight to the clock events,
            # this has two advantages:
            #
            #   1. We can calculate its duration in seconds now and check if
            #      we need more clock events.
            #
            #   2. In our entries we can also figure out the duration in
            #      seconds using the same technique as here. This is
            #      very important for creating musically useful materials.
            clock_event = clock_events.ClockEvent(
                [
                    core_events.SequentialEvent(
                        [music_events.NoteLike(pitch_list="c", duration=ev_duration)],
                        tempo_envelope=core_events.TempoEnvelope(
                            [[0, tempo], [ev_duration, tempo]]
                        ),
                    ),
                ],
            )
            clock_duration += float(clock_event.metrize(mutate=False).duration.duration)
            clock_event_list.append(clock_event)

        clock_event_list = clock_event_list[:-1]
        scale_position_count = len(clock_event_list)

        gatra_tuple = project_converters.ScaleToGatraTuple().convert(scale)
        markov_chain = project_converters.GatraTupleToMarkovChain().convert(gatra_tuple)
        markov_chain.make_deterministic_map()
        start = gatra_tuple[0]
        gatra_generator = markov_chain.walk_deterministic((start,))

        scale_position_list = []
        while len(scale_position_list) < scale_position_count:
            scale_position_list.extend(next(gatra_generator))
        scale_position_list = scale_position_list[:scale_position_count]

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
                for start_pitch, end_pitch, clock_event in zip(
                    root_pitch_tuple, root_pitch_tuple[1:], clock_event_list
                )
            ]
        )

        modal_0_sequential_event_to_clock_line = clock_converters.Modal0SequentialEventToClockLine(
            (
                diary_converters.Modal0SequentialEventToEventPlacementTuple(
                    orchestration.get_subset("AEOLIAN_HARP"),
                    # Turn off modal1 mode converter for better performance
                    # (this is very expensive and we don't want to use any
                    #  modal1 context based entries here anyway).
                    add_mod1=False,
                ),
                diary_converters.Modal0SequentialEventToEventPlacementTuple(
                    orchestration.get_subset("CLAVICHORD"),
                    add_mod1=True,
                ),
            )
        )
        main_clock_line = modal_0_sequential_event_to_clock_line.convert(
            modal_sequential_event
        )

        clock = clock_interfaces.Clock(main_clock_line)
        return clock

    def _make_empty_clock(self, duration, orchestration):
        main_clock_line = self._make_empty_clock_line(duration)
        main_clock_line.register(
            timeline_interfaces.EventPlacement(
                core_events.SimultaneousEvent(
                    [
                        core_events.TaggedSimultaneousEvent(
                            [
                                core_events.SequentialEvent(
                                    [
                                        core_events.SimpleEvent(1)
                                        for _ in range(
                                            project_parameters.AeolianHarp.TOTAL_STRING_COUNT
                                        )
                                    ]
                                )
                            ],
                            tag="aeolian harp",
                        )
                    ]
                ),
                0,
                duration,
            )
        )
        clock = clock_interfaces.Clock(main_clock_line)
        return clock

    def _make_empty_clock_line(self, duration):
        return clock_interfaces.ClockLine(
            clock_events.ClockEvent(
                [core_events.SequentialEvent([core_events.SimpleEvent(duration)])]
            )
        )
