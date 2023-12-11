import os

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import project_interfaces

import project

with diary_interfaces.open():

    path = "/".join(os.path.abspath(__file__).split("/")[:-1])

    diary_interfaces.DynamicEntry.from_file(
        "test",
        project_interfaces.ProjectContext.identifier,
        project_interfaces.PEntryReturnType,
        skip_check=project.constants.SKIP_CHECK,
        file_path=f"{path}/test.py",
        relevance=1,
    )

    diary_interfaces.DynamicEntry.from_file(
        "test1",
        project_interfaces.ProjectContext.identifier,
        project_interfaces.PEntryReturnType,
        skip_check=project.constants.SKIP_CHECK,
        file_path=f"{path}/test1.py",
        relevance=1,
    )
