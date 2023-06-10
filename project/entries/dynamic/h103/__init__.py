import os

from mutwo import diary_interfaces
from mutwo import timeline_interfaces

import project

path = "/".join(os.path.abspath(__file__).split("/")[:-1])

diary_interfaces.DynamicEntry.from_file(
    "h103s",
    diary_interfaces.H103Context.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/h130s.py",
    relevance=50,
)


diary_interfaces.DynamicEntry.from_file(
    "h103-pclock",
    diary_interfaces.H103Context.identifier,
    timeline_interfaces.EventPlacement,
    skip_check=project.constants.SKIP_CHECK,
    file_path=f"{path}/pclock.py",
    relevance=50,
)
