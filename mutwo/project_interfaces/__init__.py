import dataclasses
import typing

import ranges

from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters

# Alias
j = music_parameters.JustIntonationPitch

Voice: typing.TypeAlias = core_events.SequentialEvent[music_events.NoteLike]


@dataclasses.dataclass(frozen=True)
class TableCanon(object):

    initial_voice: Voice
    # Must be a diatonic scale where each pitch degree represents
    # one of the named pitch classes {c, d, e, f, g, a, b}
    scale: typing.Optional[music_parameters.Scale] = None

    voice0: typing.Optional[Voice] = None
    voice1: typing.Optional[Voice] = None
    voice2: typing.Optional[Voice] = None
    voice3: typing.Optional[Voice] = None

    simultaneous_event: typing.Optional[core_events.SimultaneousEvent] = None

    def __post_init__(self):
        # Sanity check for scale
        pitch_class_list = []
        assert self.scale.scale_degree_count == 7, "Must be a diatonic scale!"
        for sc in range(self.scale.scale_degree_count):
            p = self.scale.scale_index_to_pitch(sc)
            w = music_parameters.WesternPitch.from_midi_pitch_number(
                music_parameters.DirectPitch(p.frequency).midi_pitch_number
            )
            pitch_class_list.append(w.pitch_class_name)

        assert len(pitch_class_list) == len(
            set(pitch_class_list)
        ), f"Found duplicate pitch class names in {pitch_class_list}!"

        simultaneous_event = core_events.SimultaneousEvent([])
        for i in range(VOICE_COUNT):
            voice = core_events.TaggedSequentialEvent(
                getattr(self, f"_v{i}")(self.initial_voice)[:], tag=f"voice_{i}"
            )
            object.__setattr__(self, f"voice{i}", voice)
            simultaneous_event.append(voice)
        object.__setattr__(self, "simultaneous_event", simultaneous_event)

    # Initial voice -> voice

    # -> baritone clef
    def _v0(self, initial_voice: Voice):
        return initial_voice.copy()

    # -> bass clef
    def _v1(self, initial_voice: Voice):
        return baritone_to_bass(initial_voice)

    # <- baritone clef
    def _v2(self, initial_voice: Voice):
        return reverse_baritone(initial_voice, scale=self.scale)

    # <- bass clef
    def _v3(self, initial_voice: Voice):
        return baritone_to_bass(reverse_baritone(initial_voice, scale=self.scale))


VOICE_COUNT = 4


# Helper functions


def baritone_to_bass(voice: Voice):
    return voice.mutate_parameter(
        "pitch_list", lambda pl: [p.subtract(j("3/2")) for p in pl], mutate=False
    )


def reverse_baritone(
    voice: Voice,
    scale: typing.Optional[music_parameters.Scale] = None,
    center: typing.Optional[music_parameters.JustIntonationPitch] = None,
):
    if scale is not None:

        def r(p):
            return reverse_baritone_pitch_scale(p, center=center, scale=scale)

    else:

        def r(p):
            return reverse_baritone_pitch(p, center=center)

    v = voice.set_parameter("pitch_list", lambda pl: [r(p) for p in pl], mutate=False)
    v.reverse()
    return v


def reverse_baritone_pitch(
    pitch: music_parameters.JustIntonationPitch,
    center: typing.Optional[music_parameters.JustIntonationPitch] = None,
):
    center = center or j("1/2")
    assert center == music_parameters.WesternPitch("a", 3), "Bad concert pitch!"
    Δcenter = pitch - center
    return center - Δcenter


def reverse_baritone_pitch_scale(
    pitch: music_parameters.JustIntonationPitch,
    scale: music_parameters.Scale,
    center: typing.Optional[music_parameters.JustIntonationPitch] = None,
):
    center = center or j("1/2")
    assert center in ranges.Range(
        music_parameters.WesternPitch("af", 3), music_parameters.WesternPitch("as", 3)
    ), "Bad concert pitch!"
    pitch_index = scale.pitch_to_scale_index(pitch)
    center_index = scale.pitch_to_scale_index(center)
    Δcenter = pitch_index - center_index
    new_pitch_index = center_index - Δcenter
    return scale.scale_index_to_pitch(new_pitch_index)
