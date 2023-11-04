from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import mmml_converters
from mutwo import project_interfaces

import project


e2mml = mmml_converters.EventToMMMLExpression()


def main():
    context_tuple = (project_interfaces.PContext(0),)
    for context in context_tuple:
        entry_tuple = tuple(
            diary_interfaces.fetch_wrapped_entry_tree().rquery(
                context_identifier=str(context.identifier),
                return_type=core_events.SimultaneousEvent.__name__,
            )
        )
        entry = entry_tuple[0]
        sim = entry(context)
        mmml = e2mml(sim)
        with open(f"project/mmml/{context.page_index}.mmml", "w") as f:
            f.write(mmml)


with diary_interfaces.open():
    main()
