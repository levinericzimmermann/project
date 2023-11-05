import argparse

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import mmml_converters
from mutwo import project_interfaces

import project


e2mml = mmml_converters.EventToMMMLExpression()


def main(page_count):
    for i in range(page_count or project.constants.PAGE_COUNT):
        sentence = project.constants.SENTENCE_TUPLE[i]
        m, next_m = project.u.page_index_to_current_melody_and_next_melody(i)
        context = project_interfaces.PContext(i, sentence, m, next_m)
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


parser = argparse.ArgumentParser(prog="project")
parser.add_argument("-c", "--pagecount")

args = parser.parse_args()

page_count = int(args.pagecount) if args.pagecount else None

with diary_interfaces.open():
    main(page_count)
