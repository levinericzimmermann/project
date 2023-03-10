import os

import ranges

from mutwo import clock_events
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import timeline_interfaces

import project

path = "/".join(os.path.abspath(__file__).split("/")[:-1])

with diary_interfaces.open():
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
        tuple[
            music_parameters.JustIntonationPitch, music_parameters.JustIntonationPitch
        ],
        skip_check=project.constants.SKIP_CHECK,
        file_path=f"{path}/dyad.py",
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
        "two-dyads",
        diary_interfaces.ModalContext0.identifier,
        timeline_interfaces.EventPlacement,
        skip_check=project.constants.SKIP_CHECK,
        abbreviation_to_path_dict=dict(dyad=dyad.path),
        file_path=f"{path}/two-dyads.py",
        relevance=5,
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
        "natural-harmonic",
        diary_interfaces.ModalContext1.identifier,
        timeline_interfaces.EventPlacement,
        skip_check=project.constants.SKIP_CHECK,
        file_path=f"{path}/natural-harmonic.py",
        relevance=80,
    )

    # ###############################################
    # Clocks
    from .clocks import *
