import project

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="project")
    parser.add_argument("-i", "--illustration", action="store_true")
    parser.add_argument("-n", "--notation", default="")
    parser.add_argument("-s", "--sound", action="store_true")
    parser.add_argument("-m", "--max-index", default=16)

    args = parser.parse_args()
    max_index = int(args.max_index)

    if args.illustration:
        project.render.illustration(project.constants.PART_TUPLE)

    if args.sound:
        project.render.sound(
            project.constants.PART_TUPLE,
            project.constants.DURATION_TUPLE,
            project.constants.PATH_TUPLE,
            project.constants.PEOPLE_TUPLE,
        )
