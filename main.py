import argparse

import project

parser = argparse.ArgumentParser(prog="project")
parser.add_argument("-n", "--notation", action="store_true")
parser.add_argument("-s", "--sound", action="store_true")
parser.add_argument("-c", "--pagecount")

args = parser.parse_args()

page_count = int(args.pagecount) if args.pagecount else None

if args.notation:
    project.render.notation(page_count)

if args.sound:
    project.render.midi(page_count)
