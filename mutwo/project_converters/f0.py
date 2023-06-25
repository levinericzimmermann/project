import abc

import numpy as np

from mutwo import common_generators
from mutwo import core_converters
from mutwo import core_utilities
from mutwo import project_converters


# Basic parsing of converted parameters to F0 form
#
# Declare the converters as singleton


class DataToF0Event(core_converters.abc.Converter):
    def convert(self, state: int, duration: int, frequency: float, velocity: int):
        # state,duration,frequency,velocity
        return project_converters.constants.F0.PARAMETER_DELIMITER.join(
            [str(p) for p in (state, duration, frequency, velocity)]
        )


class F0EventListToF0(core_converters.abc.Converter):
    def convert(self, f0_event_list: list[str]) -> str:
        return project_converters.constants.F0.EVENT_DELIMITER.join(f0_event_list)


DATA_TO_F0_EVENT = DataToF0Event()
F0_EVENT_LIST_TO_F0 = F0EventListToF0()


# Now
#   mutwo -> f0
# parsing
#
# We have different strategies, depending on the musical material
#
#   DataToF0    (abstract)
#       DataToContinousF0       => continous tones
#       DataToPercussiveF0      => short 'staccatto' tones


class DataToF0(core_converters.abc.Converter):
    @abc.abstractmethod
    def convert(
        self, duration_tuple: tuple[int, ...], frequency: float, velocity: int
    ) -> tuple[str]:
        ...


class DataToContinousF0(DataToF0):
    def convert(
        self, duration_tuple: tuple[int, ...], frequency: float, velocity: int
    ) -> str:
        event_count = len(duration_tuple)

        # If we do have enough events we'll interpolate to our max
        # volume to make a rising/falling envelope.
        # This is necessary, because the DSP of the Arduino (f0.ino)
        # doesn't do this by itself.
        v_tuple = tuple(velocity for _ in duration_tuple)
        if event_count >= 3 and frequency != 0:
            min_v = min((project_converters.constants.F0.MIN_VELOCITY, velocity))
            left, center, right = common_generators.euclidean(event_count, 3)
            v_tuple = (
                tuple(np.geomspace(min_v, velocity, left, dtype=int))
                + tuple(velocity for _ in range(center))
                + tuple(np.geomspace(velocity, min_v, right, dtype=int))
            )

        assert len(v_tuple) == event_count

        e_list = []

        max_index = len(duration_tuple) - 1
        for index, ed in enumerate(duration_tuple):
            if index == 0:
                state = project_converters.constants.F0.STATE_NEW
            elif index == max_index:
                state = project_converters.constants.F0.STATE_STOP
            else:
                state = project_converters.constants.F0.STATE_KEEP

            e_list.append(DATA_TO_F0_EVENT(state, ed, frequency, v_tuple[index]))

        return F0_EVENT_LIST_TO_F0(e_list)


class DataToPercussiveF0(core_converters.abc.Converter):
    def convert(
        self, duration_tuple: tuple[int, ...], frequency: float, velocity: int
    ) -> str:
        # We only need one active event & we can set everything else to 'Rest'
        e_list = [
            DATA_TO_F0_EVENT(
                project_converters.constants.F0.STATE_NEW,
                duration_tuple[0],
                frequency,
                velocity,
            )
        ]
        for d in duration_tuple[1:]:
            e_list.append(
                DATA_TO_F0_EVENT(project_converters.constants.F0.STATE_STOP, d, 0, 0)
            )
        return F0_EVENT_LIST_TO_F0(e_list)


class EventToF0(core_converters.abc.EventConverter):
    def __init__(
        self,
        data_to_continous_f0: DataToContinousF0 = DataToContinousF0(),
        data_to_percussive_f0: DataToPercussiveF0 = DataToPercussiveF0(),
    ):
        self._data_to_continous_f0 = data_to_continous_f0
        self._data_to_percussive_f0 = data_to_percussive_f0

    def convert(self, event_to_convert):
        return self._convert_event(event_to_convert, 0)[0]

    def _convert_simple_event(self, event_to_convert, absolute_entry_delay):
        e = event_to_convert

        d = int(round(float(e.duration) * 1000))
        d_tuple = common_generators.euclidean(
            d, max((d // project_converters.constants.F0.MAX_DURATION, 2))
        )

        try:
            f = round(e.pitch_list[0].frequency, 2)
        except (AttributeError, IndexError):
            f = 0

        try:
            v = e.volume.midi_velocity
        except AttributeError:
            v = 0
        else:
            v = int(core_utilities.scale(v, 0, 127, 0, 255))

        data = (d_tuple, f, v)

        return (self._data_to_continous_f0(*data),)

    def _convert_sequential_event(self, *args, **kwargs):
        return (
            F0_EVENT_LIST_TO_F0(super()._convert_sequential_event(*args, **kwargs)),
        )

    def _convert_simultaneous_event(
        self,
        e,
        absolute_entry_delay,
        depth,
    ):
        if (ecount := len(e)) == 1:
            return self._convert_event(e[0], absolute_entry_delay, depth)
        elif ecount == 0:
            return tuple([])
        raise NotImplementedError("f0 doesn't support simultaneous events!")
