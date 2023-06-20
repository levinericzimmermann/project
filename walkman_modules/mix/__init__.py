import functools
import operator

import numpy as np
import pyo
import walkman

MAX_INPUT_CHANNEL_COUNT = 10


class Diffusion(
    walkman.ModuleWithDecibel,
    **{
        f"audio_input_{index}": walkman.Catch(
            walkman.constants.EMPTY_MODULE_INSTANCE_NAME, implicit=False
        )
        for index in range(MAX_INPUT_CHANNEL_COUNT)
    },
):
    """Diffuse multiple sources over a set of loudspeakers.

    The idea is to unify a set of disparate instruments into one common sound.
    But this common sound shouldn't be "static" or "flat", but constantly in
    flux. So it's basically a random multi-panner of multi-sources.

    The question is:

        - how can we keep a balanced sound (e.g. balance between different
          instruments) while at the same time constantly changing the
          amplification distribution?
        - or in other words: how can we ensure two distributions create an
          equal sonic loudness?

        for instance

            1   =>  low/middle/high     low/middle/high     low/middle/high
                    1                   2                   3

        and now we have

            1   =>  low                 low                 high
                    1                   2                   3

        which should be equally loud as

            1   =>  middle              low                 middle
                    1                   2                   3

        - we could use multiple instances of a pyo.Pan object, where
          each 'Pan' object has a constant volume, but then moves in a
          different way?
        - so we'd have pan_low, pan_middle, pan_high?
        - & then we can also vary the "spread" factor of pyo.Pan, can't we?
    """

    def __init__(
        self,
        *args,
        input_channel_count: int = 1,
        output_channel_count: int = 2,
        pan_decibel: float = 0,
        base_decibel: float = -12,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        assert (
            output_channel_count > 1
        ), "Need more than one channel in order to diffuse them"
        self.output_channel_count = output_channel_count
        assert (
            input_channel_count < MAX_INPUT_CHANNEL_COUNT
        ), "More than max input channels!"
        assert input_channel_count > 0, "Too few input channels"
        self.input_channel_count = input_channel_count
        self._random = np.random.default_rng(seed=10)
        self.base_amp = decibel2amp(base_decibel)
        self.pan_amp = decibel2amp(pan_decibel)

    def _setup_pyo_object(self):
        super()._setup_pyo_object()

        self.mixer = pyo.Mixer(chnls=1, outs=self.output_channel_count)

        pan_list = []
        pyo_object_list = []
        for i in range(self.input_channel_count):
            audio_input = getattr(self, f"audio_input_{i}").pyo_object

            self.mixer.addInput(i, audio_input)
            for n in range(self.output_channel_count):
                self.mixer.setAmp(i, n, self.base_amp)

            meta_pan_control = pyo.LFO(
                freq=self._random.uniform(0.01, 0.05), add=1.01, mul=0.45, type=3
            )
            pan_control = pyo.LFO(freq=meta_pan_control, add=1, mul=0.5, type=3)
            spread_control = pyo.Randi(freq=self._random.uniform(0.15, 0.3))
            pan = pyo.Pan(
                audio_input,
                pan=pan_control,
                spread=spread_control,
                outs=self.output_channel_count,
                mul=self.pan_amp,
            )
            pan_list.append(pan)
            pyo_object_list.extend([pan_control, meta_pan_control, pan, spread_control])

        self.summed_mixer = PyoObjectMixer([channel[0] for channel in self.mixer])

        self.summed = (
            functools.reduce(operator.add, pan_list) + self.summed_mixer
        ) * self.amplitude_signal_to
        pyo_object_list.extend([self.summed, self.mixer, self.summed_mixer])

        self.internal_pyo_object_list.extend(pyo_object_list)

    @functools.cached_property
    def _pyo_object(self):
        return self.summed


class PyoObjectMixer(pyo.PyoObject):
    def __init__(self, base_objs: list):
        super().__init__()
        self._base_objs = base_objs


def decibel2amp(decibel):
    return float(1 * (10 ** (decibel / 20)))
