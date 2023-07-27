import itertools
import subprocess

import numpy as np

from mutwo import common_generators
from mutwo import core_generators
from mutwo import core_converters
from mutwo import core_events
from mutwo import csound_converters
from mutwo import music_events
from mutwo import music_parameters


duration = 60 * 5  # 5 minutes


class PitchTupleToSoundFile(csound_converters.EventToSoundFile):
    AMBITUS = music_parameters.OctaveAmbitus(
        music_parameters.JustIntonationPitch("4/5"),
        music_parameters.JustIntonationPitch("2/1"),
    )

    def __init__(self):
        def getpitch(note):
            try:
                return note.pitch_list[0].frequency
            except IndexError:
                raise AttributeError

        super().__init__(
            "etc/csound/sine.orc",
            csound_converters.EventToCsoundScore(
                p4=getpitch, p5=lambda n: n.volume.amplitude
            ),
            remove_score_file=True,
        )
        self._random = np.random.default_rng(20)
        self._activity_level = common_generators.ActivityLevel()

    def convert(self, pitch_tuple, path):
        dynamic_choice = core_generators.DynamicChoice(
            pitch_tuple,
            (
                core_events.Envelope([[0, 1], [1, 0]]),
                core_events.Envelope([[0, 0], [1, 1]]),
            ),
        )

        sequential_event = core_events.SequentialEvent([])
        while sequential_event.duration < duration:
            # +20 because the position shouldn't be only about the
            # start point, but also about the end point, otherwise
            # the first harmony is always longer than the second
            # harmony.
            position = (sequential_event.duration + 20) / duration
            if self._activity_level(3):
                pitch = self._random.choice(
                    self.AMBITUS.get_pitch_variant_tuple(
                        dynamic_choice.gamble_at(position)
                    )
                )
                drange = (30, 100)
            else:
                pitch = None
                drange = (15, 50)
            note_duration = self._random.uniform(*drange)
            if self._activity_level(5):
                decibel = -12
            else:
                decibel = -36
            if not pitch:
                decibel = -100
            note = music_events.NoteLike(
                pitch,
                duration=note_duration,
                volume=music_parameters.DecibelVolume(decibel),
            )
            sequential_event.append(note)

        sequential_event.cut_out(0, duration)

        if not (pl := sequential_event[-1].pitch_list):
            pl.append(pitch_tuple[-1])

        v = super().convert(sequential_event, path)
        mp3path = ".".join(path.split(".")[:-1]) + ".mp3"
        subprocess.call(
            [
                "ffmpeg",
                "-i",
                path,
                "-vn",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-b:a",
                "64k",
                mp3path,
            ]
        )
        return v


class HarmonyTupleToSoundFileTuple(core_converters.abc.Converter):
    def __init__(self):
        self._pitch_tuple_to_sound_file = PitchTupleToSoundFile()

    def convert(self, harmony_tuple, index):
        for i, pitch_tuple in enumerate(itertools.product(*harmony_tuple)):
            path = f"builds/sound/s{index}_{i}.wav"
            self._pitch_tuple_to_sound_file(pitch_tuple, path)
