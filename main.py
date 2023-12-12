import project  # sideeffects

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import project_interfaces

with diary_interfaces.open():
    entry_tuple = tuple(diary_interfaces.fetch_wrapped_entry_tree().rquery())
    test1 = entry_tuple[-1]
    c = project_interfaces.ProjectContext()
    data = test1(c)

event_tuple = (data[0],)

event = core_events.SimultaneousEvent(
    [
        core_events.TaggedSequentialEvent([], tag="v"),
        core_events.TaggedSequentialEvent([], tag="r"),
    ]
)

for i, e in enumerate(event_tuple):
    # Add electronic cue to notation
    pic = e["v"][0].playing_indicator_collection
    pic.cue.index = i + 1

    # Add breath symbols to notation
    for i, breath in enumerate(e["b"]):
        e["v"].get_event_at(
            i
        ).playing_indicator_collection.breath_indicator.breath = breath.breath_or_hold_breath

    # Extend to previous structure
    event["v"].extend(e["v"])
    event["r"].extend(e["r"].chordify())

project.render.notate(event)
