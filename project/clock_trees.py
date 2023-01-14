import numpy as np
import ranges
import typing

from mutwo import clock_converters
from mutwo import clock_events
from mutwo import clock_generators
from mutwo import music_events
from mutwo import music_parameters

import project


pCy = clock_generators.PickSampleByCycle


def no(
    *args,
    mutate_p: typing.Callable[
        [music_parameters.PlayingIndicatorCollection], type[None]
    ] = lambda p: None,
    mutate_n: typing.Callable[
        [music_parameters.NotationIndicatorCollection], type[None]
    ] = lambda n: None,
    **kwargs
) -> music_events.NoteLike:
    n = music_events.NoteLike(*args, **kwargs)
    mutate_p(n.playing_indicator_collection)
    mutate_n(n.playing_indicator_collection)
    return n


def sett(flag_count: int, dynamic=None):
    def _(p):
        p.tremolo.flag_count = flag_count
        p.tremolo.dynamic = dynamic
        assert p.tremolo.is_active

    return _


class DefaultPicker(object):
    def __init__(self, seed: int = 1031, p=None):
        self.p = p
        self._random = np.random.default_rng(seed)

    def __call__(self, event_count_tuple):
        return self._random.choice(event_count_tuple, p=self.p)


DP = DefaultPicker


def get_clock_tree():
    ct = clock_generators.ClockTree(identifier="simple")
    n = ct.create_layer
    o = project.constants.ORCHESTRATION_CLOCK
    n(
        "root",
        None,
        pCy(
            (
                no(
                    duration=3,
                    instrument_list=[o.CLOCK_I0],
                    volume="p",
                    mutate_p=lambda p: (sett(16, music_parameters.Tremolo.D.AccRit)(p)),
                ),
                no(duration=2),
                no(duration=5, instrument_list=[o.CLOCK_I0], volume="mf"),
                no(duration=1),
                no(
                    duration=7,
                    instrument_list=[o.CLOCK_I0],
                    volume="p",
                    mutate_p=lambda p: (sett(16, music_parameters.Tremolo.D.Rit)(p)),
                ),
                no(duration=2),
            )
        ),
        pCy(),
        pick_event_count=DP(),
    )
    n(
        "l1",
        "root",
        pCy(
            (
                no(duration=1, instrument_list=[o.CLOCK_I1], volume="pp"),
                no(duration=3),
                no(duration=2, instrument_list=[o.CLOCK_I1], volume="mf"),
                no(
                    duration=3,
                    instrument_list=[o.CLOCK_I1],
                    volume="pp",
                    mutate_p=lambda p: (sett(16, music_parameters.Tremolo.D.Rit)(p)),
                ),
                no(duration=1, instrument_list=[o.CLOCK_I1], volume="pp"),
                no(duration=2),
            )
        ),
        pCy(),
        ranges.Range(4, 5),
        DP(),
    )
    # n(
    #     "l2",
    #     "l1",
    #     pCy(
    #         (
    #             no(duration=3, instrument_list=o.CLOCK_I2),
    #             no(duration=0.75, instrument_list=o.CLOCK_I2),
    #         )
    #     ),
    #     pCy(),
    #     ranges.Range(1, 2),
    #     DP(),
    # )
    # n(
    #     "l3",
    #     "l2",
    #     pCy(
    #         (
    #             no(duration=0.5, instrument_list=o.CLOCK_I4),
    #             no(duration=2),
    #             no(duration=0.35, instrument_list=o.CLOCK_I3),
    #         )
    #     ),
    #     pCy(),
    #     ranges.Range(0, 2),
    #     DP(p=(0.75, 0.25)),
    # )
    return ct


class ModalEvent0ToClockTree(clock_converters.ModalEvent0ToClockTree):
    def __init__(self, scale):
        self._scale = scale
        self._clock_tree = get_clock_tree()

    def convert(
        self, modal_event_to_convert: clock_events.ModalEvent0
    ) -> clock_generators.ClockTree:
        return self._clock_tree
