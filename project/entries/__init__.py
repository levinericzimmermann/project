import os

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import project_interfaces

import project

with diary_interfaces.open():

    path = "/".join(os.path.abspath(__file__).split("/")[:-1])

    simple = diary_interfaces.DynamicEntry.from_file(
        "simple",
        project_interfaces.PContext.identifier,
        core_events.SimultaneousEvent,
        skip_check=project.constants.SKIP_CHECK,
        file_path=f"{path}/simple.py",
        relevance=1,
    )
