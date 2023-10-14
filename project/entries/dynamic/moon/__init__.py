import os

from mutwo import diary_interfaces
from mutwo import timeline_interfaces

import project

path = "/".join(os.path.abspath(__file__).split("/")[:-1])

diary_interfaces.DynamicEntry.from_file(
    "mpi6",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi6.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi4",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi4.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi3",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi3.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi2",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi2.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi1",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi0.py",
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
)

diary_interfaces.DynamicEntry.from_file(
    "mpi22",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi22.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi21",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi21.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi20",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi20.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi29",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi29.py",
    relevance=100,
)

diary_interfaces.DynamicEntry.from_file(
    "mpi28",
    diary_interfaces.MoonContext.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/mpi28.py",
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
