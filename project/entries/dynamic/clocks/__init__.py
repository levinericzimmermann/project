import os

from quicktions import Fraction as f
import ranges

from mutwo import clock_events
from mutwo import core_parameters
from mutwo import diary_interfaces
from mutwo import music_events
from mutwo import timeline_interfaces

import project

path = "/".join(os.path.abspath(__file__).split("/")[:-1])


# ###############################################
# Clocks
# ###############################################

d = core_parameters.DirectDuration


# ###############################################
# Helper entries (for common problems)
# ###############################################

note = diary_interfaces.DynamicEntry.from_file(
    "note",
    diary_interfaces.EmptyContext.identifier,
    music_events.NoteLike,
    skip_check=project.constants.SKIP_CHECK_CLOCK,
    file_path=f"{path}/note.py",
    comment=r"Build one note. Common utility for clock",
)

clock_event = diary_interfaces.DynamicEntry.from_file(
    "clock",
    diary_interfaces.EmptyContext.identifier,
    clock_events.ClockEvent,
    skip_check=project.constants.SKIP_CHECK_CLOCK,
    file_path=f"{path}/clock.py",
    comment=r"Create ClockEvent([SequentialEvent([...])]) from event list.",
)

tremolo = diary_interfaces.ClockEntry.from_file(
    "tremolo",
    skip_check=project.constants.SKIP_CHECK_CLOCK,
    file_path=f"{path}/tremolo.py",
    duration_range=ranges.Range(d(f(16, 16)), d(f(28, 16))),
    abbreviation_to_path_dict=dict(note=note.path, clock=clock_event.path),
)

# ###############################################
# Musical entries to be used.
# ###############################################

tremolo_long = diary_interfaces.ClockEntry.from_file(
    "tremolo_long",
    skip_check=project.constants.SKIP_CHECK_CLOCK,
    file_path=f"{path}/tremolo_long.py",
    duration_range=ranges.Range(d(f(26, 16)), d(f(44, 16))),
    abbreviation_to_path_dict=dict(tremolo=tremolo.path),
)

tremolo_middle = diary_interfaces.ClockEntry.from_file(
    "tremolo_middle",
    skip_check=project.constants.SKIP_CHECK_CLOCK,
    file_path=f"{path}/tremolo_middle.py",
    duration_range=ranges.Range(d(f(18, 16)), d(f(32, 16))),
    abbreviation_to_path_dict=dict(tremolo=tremolo.path),
)

grace = diary_interfaces.ClockEntry.from_file(
    "grace",
    skip_check=project.constants.SKIP_CHECK_CLOCK,
    file_path=f"{path}/grace.py",
    duration_range=ranges.Range(d(f(20, 16)), d(f(26, 16))),
    abbreviation_to_path_dict=dict(note=note.path, clock=clock_event.path),
)

hit = diary_interfaces.ClockEntry.from_file(
    "hit",
    skip_check=project.constants.SKIP_CHECK_CLOCK,
    file_path=f"{path}/hit.py",
    duration_range=ranges.Range(d(f(13, 16)), d(f(20, 16))),
    abbreviation_to_path_dict=dict(note=note.path, clock=clock_event.path),
)

# ###############################################
# Modal context.
# ###############################################

diary_interfaces.DynamicEntry.from_file(
    "clock_modal0",
    diary_interfaces.ModalContext1.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/modal0.py",
    abbreviation_to_path_dict=dict(
        tremolo_middle=tremolo_middle.path,
        tremolo_long=tremolo_long.path,
        grace=grace.path,
        hit=hit.path,
    ),
    # relevance=90,
    relevance=120,
)
