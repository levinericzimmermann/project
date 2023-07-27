from mutwo import music_parameters

import project

j = music_parameters.JustIntonationPitch

part_tuple = tuple(
    ((j("1/1"), j("3/4"), j("7/6")), (j("1/1"), j("2/3"), j("9/8"))) for _ in range(7)
)


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
        project.render.illustration(part_tuple)

    if args.sound:
        project.render.sound(part_tuple)
