import project  # sideeffects

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import project_interfaces

with diary_interfaces.open():
    entry_tuple = tuple(diary_interfaces.fetch_wrapped_entry_tree().rquery())
    test1 = entry_tuple[-1]
    c = project_interfaces.ProjectContext()
    data = test1(c)


data_tuple = (data,)
project.render.notate(data_tuple)
