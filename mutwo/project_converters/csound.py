import concurrent.futures
import os
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

    def convert(self, pitch_tuple, path, duration, duration_per_harmony):
        sequential_event = self._get_sequential_event(
            pitch_tuple, duration, duration_per_harmony
        )

        super().convert(sequential_event, path)
        return self._render_mp3(path)

    def _get_sequential_event(self, pitch_tuple, duration, duration_per_harmony):
        interpolation_list = []
        for p0, p1 in zip(pitch_tuple, pitch_tuple[1:]):
            dynamic_choice = core_generators.DynamicChoice(
                (p0, p1),
                (
                    core_events.Envelope([[0, 1], [1, 0]]),
                    core_events.Envelope([[0, 0], [1, 1]]),
                ),
            )
            interpolation_list.append(dynamic_choice)

        harmony_tick_event = core_events.SequentialEvent(
            [core_events.SimpleEvent(d) for d in duration_per_harmony]
        )
        abs_tt = harmony_tick_event.absolute_time_tuple

        sequential_event = core_events.SequentialEvent([])
        while sequential_event.duration < duration:
            d = sequential_event.duration
            harmony_tick_index = harmony_tick_event.get_event_index_at(d)
            c = harmony_tick_index // 2
            if harmony_tick_index % 2 == 0:
                pitch = pitch_tuple[c]
            else:
                interpolation_dur = duration_per_harmony[harmony_tick_index]
                position = (d - abs_tt[harmony_tick_index]) / interpolation_dur
                pitch = dynamic_choice.gamble_at(position)

            pitch = self._random.choice(self.AMBITUS.get_pitch_variant_tuple(pitch))
            drange = (30, 100)
            if not self._activity_level(3):
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

        return sequential_event

    def _render_mp3(self, path):
        mp3path = ".".join(path.split(".")[:-1]) + ".mp3"
        try:
            os.remove(mp3path)
        except FileNotFoundError:
            pass
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
        return mp3path


class HarmonyTupleToSoundFileTuple(core_converters.abc.Converter):
    def __init__(self):
        self._pitch_tuple_to_sound_file = PitchTupleToSoundFile()

    def convert(self, part, index, duration, people_tuple) -> dict:
        harmony_tuple, duration_per_harmony = part
        assert (
            sum(duration_per_harmony) == duration
        ), f"inconsistent duration: {duration_per_harmony} != {duration}"
        harmony_list = [list(h) for h in harmony_tuple]
        max_pitch_count = max(len(h) for h in harmony_tuple)
        for h in harmony_list:
            p_cycle = itertools.cycle(h)
            while len(h) < max_pitch_count:
                h.append(next(p_cycle))
        pitch_tuple_combination_cycle = itertools.cycle(tuple(zip(*harmony_list)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            person_to_future = {}
            for person in people_tuple:
                pitch_tuple = next(pitch_tuple_combination_cycle)
                path = f"builds/sound/{index}_{person}.wav"
                future = pool.submit(
                    self._pitch_tuple_to_sound_file,
                    pitch_tuple,
                    path,
                    duration,
                    duration_per_harmony,
                )
                person_to_future[person] = future
            person_to_path = {}
            for person, future in person_to_future.items():
                mp3path = future.result()
                person_to_path[person] = mp3path
        return person_to_path
