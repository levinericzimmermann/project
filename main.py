import argparse

from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import project_interfaces

import project

with diary_interfaces.open():
    entry_tuple = tuple(diary_interfaces.fetch_wrapped_entry_tree().rquery())
    test1 = entry_tuple[-1]
    c = project_interfaces.ProjectContext()
    data = test1(c)

data_tuple = (data,)

parser = argparse.ArgumentParser(prog="project")
parser.add_argument("-n", "--notation", action="store_true")
parser.add_argument("-m", "--midi", action="store_true")

args = parser.parse_args()

if args.notation:
    project.render.notate(data_tuple)

if args.midi:
    project.render.midi(data_tuple)
