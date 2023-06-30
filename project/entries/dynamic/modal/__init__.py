import os

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import timeline_interfaces

import project

path = "/".join(os.path.abspath(__file__).split("/")[:-1])

# ###############################################
# Requirements
# ###############################################

scale = diary_interfaces.DynamicEntry.from_file(
    "scale",
    diary_interfaces.ModalContext0.identifier,
    tuple[music_parameters.abc.Pitch, ...],
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/scale.py",
    relevance=1,
)

dyad = diary_interfaces.DynamicEntry.from_file(
    "dyad",
    diary_interfaces.ModalContext0.identifier,
    tuple[music_parameters.JustIntonationPitch, music_parameters.JustIntonationPitch],
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/dyad.py",
    relevance=1,
)

alternating_scale_chords = diary_interfaces.DynamicEntry.from_file(
    "alternating-scale-chords",
    diary_interfaces.ModalContext0.identifier,
    tuple[tuple[music_parameters.abc.Pitch, ...], ...],
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/alternating-scale-chords.py",
    abbreviation_to_path_dict=dict(scale=scale.path),
    relevance=1,
)

scale_harp = diary_interfaces.DynamicEntry.from_file(
    "scale-harp",
    diary_interfaces.ModalContext0.identifier,
    tuple[tuple[music_parameters.abc.Pitch, ...], ...],
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/scale-harp.py",
    abbreviation_to_path_dict=dict(scale=scale.path, dyad=dyad.path),
    relevance=1,
)

still = diary_interfaces.DynamicEntry.from_file(
    "still",
    diary_interfaces.ModalContext1.identifier,
    core_events.SimultaneousEvent,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/still.py",
    relevance=80,
)

# ###############################################
# Events
# ###############################################

diary_interfaces.DynamicEntry.from_file(
    "scale-event-harp",
    diary_interfaces.ModalContext0.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    abbreviation_to_path_dict=dict(scale_harp=scale_harp.path),
    file_path=f"{path}/scale-event-harp.py",
    relevance=50,
)


diary_interfaces.DynamicEntry.from_file(
    "scale-event-v",
    diary_interfaces.ModalContext0.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/scale-event-v.py",
    relevance=50,
)


diary_interfaces.DynamicEntry.from_file(
    "scale-event-g",
    diary_interfaces.ModalContext0.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    abbreviation_to_path_dict=dict(scale=scale.path),
    file_path=f"{path}/scale-event-g.py",
    relevance=100,
)


diary_interfaces.DynamicEntry.from_file(
    "scale-event-chord-instruments",
    diary_interfaces.ModalContext0.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/scale-event-chord-instruments.py",
    abbreviation_to_path_dict=dict(
        alternating_scale_chords=alternating_scale_chords.path
    ),
    relevance=5,
)

diary_interfaces.DynamicEntry.from_file(
    "two-dyads",
    diary_interfaces.ModalContext0.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    abbreviation_to_path_dict=dict(dyad=dyad.path),
    file_path=f"{path}/two-dyads.py",
    relevance=35,
)

diary_interfaces.DynamicEntry.from_file(
    "modal-silence",
    diary_interfaces.ModalContext0.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/silence.py",
    relevance=10,
)


diary_interfaces.DynamicEntry.from_file(
    "modal-1-silence",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/silence.py",
    relevance=20,
)

diary_interfaces.DynamicEntry.from_file(
    "natural-harmonic",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/natural-harmonic.py",
    relevance=80,
)


diary_interfaces.DynamicEntry.from_file(
    "still_glockenspiel",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    abbreviation_to_path_dict=dict(still=still.path),
    file_path=f"{path}/still_glockenspiel.py",
    relevance=0,
)


diary_interfaces.DynamicEntry.from_file(
    "bowed_tone_glockenspiel",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/bowed-tone-glockenspiel.py",
    relevance=70,
)

diary_interfaces.DynamicEntry.from_file(
    "bowed_tone_harp",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/bowed-tone-harp.py",
    relevance=80,
)


diary_interfaces.DynamicEntry.from_file(
    "pattern",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/pattern.py",
    relevance=2,
)


diary_interfaces.DynamicEntry.from_file(
    "explicit-silence-0",
    diary_interfaces.ModalContext0.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/explicit-silence.py",
    relevance=10000,
)


diary_interfaces.DynamicEntry.from_file(
    "explicit-silence-1",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/explicit-silence.py",
    relevance=10000,
)


diary_interfaces.DynamicEntry.from_file(
    "v_noise_0",
    diary_interfaces.ModalContext0.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/v_noise.py",
    relevance=3,
)


diary_interfaces.DynamicEntry.from_file(
    "v_noise_1",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/v_noise.py",
    relevance=5,
)


diary_interfaces.DynamicEntry.from_file(
    "g_noise_0",
    diary_interfaces.ModalContext0.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/g_noise.py",
    relevance=50,
)


diary_interfaces.DynamicEntry.from_file(
    "g_noise_1",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/g_noise.py",
    relevance=50,
)


diary_interfaces.DynamicEntry.from_file(
    "harp_noise_0",
    diary_interfaces.ModalContext0.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/harp_noise.py",
    relevance=5,
)


diary_interfaces.DynamicEntry.from_file(
    "harp_noise_1",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/harp_noise.py",
    relevance=207,
)
