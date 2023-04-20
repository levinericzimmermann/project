import os

from mutwo import diary_interfaces
from mutwo import timeline_interfaces

import project

path = "/".join(os.path.abspath(__file__).split("/")[:-1])

diary_interfaces.DynamicEntry.from_file(
    "mpi28",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi28.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi24",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi24.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi23",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi23.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi14",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi14.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi10",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi10.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi9",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi9.py",
    relevance=100,
)
