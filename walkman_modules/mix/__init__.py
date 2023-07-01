from __future__ import annotations
import functools
import operator
import typing

import numpy as np
import pyo
import walkman

MAX_INPUT_CHANNEL_COUNT = 5


class Diffusion(
    walkman.ModuleWithDecibel,
    **{
        f"audio_input_{index}": walkman.Catch(
            # set implicit=True so that it's sufficient to activate 'Diffusion' in order
            # to run all inputs.
            walkman.constants.EMPTY_MODULE_INSTANCE_NAME,
            implicit=True,
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


# Please see https://cnmat.berkeley.edu/sites/default/files/patches/Picture%203_0.png
Frequency = float
Amplitude = float
DecayRate = float
ResonatorConfiguration = typing.Tuple[Frequency, Amplitude, DecayRate]
FilePath = str
SliceIndex = int
ResonanceConfigurationFilePathList = typing.List[
    typing.Union[
        typing.Tuple[Amplitude, FilePath], typing.Tuple[Amplitude, FilePath, SliceIndex]
    ]
]


class Resonator(
    walkman.ModuleWithDecibel,
    decibel=walkman.AutoSetup(walkman.Parameter),
    audio_input=walkman.Catch(walkman.constants.EMPTY_MODULE_INSTANCE_NAME),
):
    def __init__(
        self,
        resonance_configuration_file_path_list: ResonanceConfigurationFilePathList,
        input_index: int = 0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_index = input_index
        self.resonator_configuration_tuple = (
            self.parse_resonance_configuration_file_path_list(
                resonance_configuration_file_path_list
            )
        )

    @staticmethod
    def parse_resonance_configuration_file_path_list(
        resonance_configuration_file_path_list: ResonanceConfigurationFilePathList,
    ) -> typing.Tuple[
        typing.Tuple[Amplitude, typing.Tuple[ResonatorConfiguration, ...]]
    ]:
        resonator_configuration_list = []
        for data in resonance_configuration_file_path_list:
            try:
                amplitude, resonance_configuration_file_path, slice_index = data
            except ValueError:
                amplitude, resonance_configuration_file_path = data
                slice_index = 1
            resonance_configuration_tuple = (
                Resonator.parse_resonance_configuration_file(
                    resonance_configuration_file_path
                )
            )[::slice_index]
            resonator_configuration_list.append(
                (amplitude, resonance_configuration_tuple)
            )
        return tuple(resonator_configuration_list)

    @staticmethod
    def parse_resonance_configuration_file(
        resonance_configuration_file_path: str,
    ) -> typing.Tuple[ResonatorConfiguration, ...]:
        with open(
            resonance_configuration_file_path, "r"
        ) as resonance_configuration_file:
            configuration_content = resonance_configuration_file.read()

        resonance_configuration_list = []
        for configuration_line in configuration_content.splitlines():
            try:
                _, data = configuration_line.replace(";", "").split(",")
            except ValueError:
                continue
            frequency, amplitude, decay = (
                float(value) for value in filter(bool, data.split(" "))
            )
            resonance_configuration_list.append((frequency, amplitude, decay))
        # XXX: We need set because in the text files are duplicates.
        return tuple(set(resonance_configuration_list))

    def _setup_pyo_object(self):
        super()._setup_pyo_object()
        # XXX: It's better to apply amplitude on input instead
        # on resonators, for less sudden fade in.
        self.audio_input_with_applied_decibel = self.audio_input.pyo_object[
            self.input_index
        ]
        self.resonator_list = []
        for (
            amplitude,
            resonance_configuration_tuple,
        ) in self.resonator_configuration_tuple:
            frequency_list, amplitude_list, decay_list = (
                list(value_list) for value_list in zip(*resonance_configuration_tuple)
            )
            complex_resonator = pyo.ComplexRes(
                self.audio_input_with_applied_decibel,
                freq=frequency_list,
                decay=decay_list,
                mul=amplitude_list,
            ).stop()
            mixed_resonator = complex_resonator.mix(1)
            if amplitude != 1:
                complex_resonator_with_applied_amplitude = mixed_resonator * amplitude
            else:
                complex_resonator_with_applied_amplitude = mixed_resonator
            self.resonator_list.append(complex_resonator_with_applied_amplitude)
            self.internal_pyo_object_list.append(complex_resonator)

        self.summed_resonator = sum(self.resonator_list) * self.amplitude_signal_to

        internal_pyo_object_list = [
            self.summed_resonator,
            self.audio_input_with_applied_decibel,
        ] + self.resonator_list

        self.internal_pyo_object_list.extend(internal_pyo_object_list)

    @property
    def _pyo_object(self) -> pyo.PyoObject:
        return self.summed_resonator


class SoundFilePlayer(
    walkman.ModuleWithDecibel,
    previous_path=walkman.Catch(walkman.constants.EMPTY_MODULE_INSTANCE_NAME),
    next_path=walkman.Catch(walkman.constants.EMPTY_MODULE_INSTANCE_NAME),
):
    def __init__(
        self,
        path_list: list[str],
        **kwargs,
    ):
        super().__init__(**kwargs)
        assert path_list
        self._path_list = path_list
        self._max_path_index = len(self._path_list)
        self._path_index = 0
        self._path = self._path_list[self._path_index]

    def _next(self):
        self._path_index = (self._path_index + 1) % self._max_path_index
        self._set_sound_file()

    def _previous(self):
        self._path_index = (self._path_index - 1) % self._max_path_index
        self._set_sound_file()

    def _set_sound_file(self):
        self._path = self._path_list[self._path_index]
        if does_play := self._sound_file_player.isPlaying():
            self._sound_file_player.stop()
        walkman.constants.LOGGER.info(
            f"set sound file of '{self.replication_key}' to '{self._path}'"
        )
        self._sound_file_player.setPath(self._path)
        if does_play:
            self._sound_file_player.play()

    def _setup_pyo_object(self):
        super()._setup_pyo_object()
        self._sound_file_player = pyo.SfPlayer(
            self._path, mul=self.amplitude_signal_to, interp=1, loop=True
        )
        self._change_previous = pyo.Change(self.previous_path.pyo_object).play()
        self._trigger_previous = pyo.TrigFunc(self._change_previous, self._previous).play()
        self._change_next = pyo.Change(self.next_path.pyo_object).play()
        self._trigger_next = pyo.TrigFunc(self._change_next, self._next).play()
        self.internal_pyo_object_list.extend(
            [
                # CONTROL TRIGGER SHOULD ALWAYS RUN, AND DON'T
                # CARE ABOUT WHETHER CUE IS RUNNING OR NOT.
                #     self._trigger_next,
                #     self._trigger_previous,
                #     self._change_next,
                #     self._change_previous,
                self._sound_file_player,
            ]
        )

    @property
    def _pyo_object(self) -> pyo.PyoObject:
        return self._sound_file_player
