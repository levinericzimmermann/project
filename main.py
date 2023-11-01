import argparse

import project

parser = argparse.ArgumentParser(prog="project")
parser.add_argument("-n", "--notation", action="store_true")
parser.add_argument("-s", "--sound", action="store_true")

args = parser.parse_args()

if args.notation:
    project.render.notation()

if args.sound:
    project.render.midi()
