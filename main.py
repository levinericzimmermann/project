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

    from mutwo import project_interfaces, core_events
    from mutwo.music_events import NoteLike as n
    from mutwo.music_parameters import RepeatingScaleFamily, Scale, JustIntonationPitch

    j = JustIntonationPitch

    scale = Scale(
        j("1/1"),
        RepeatingScaleFamily(
            (j("1/1"), j("9/8"), j("5/4"), j("4/3"), j("3/2"), j("5/3"), j("7/4")),
            j("2/1"),
        ),
    )

    table_canon = project_interfaces.TableCanon(
        core_events.SequentialEvent(
            [
                n([], 2),
                n("1/2", 2),
                n("9/16"),
                n("7/16"),
                n("5/8", 2),
                n([], 2),
                n("1/2", 2),
                n("7/16", 2),
                n("1/2", 2),
                n([], 2),
            ]
        ),
        scale=scale,
    )

    if args.illustration:
        project.render.illustration()

    # if args.notation:
    #     project.render.notation(clock_tuple, args.notation)

    if args.sound:
        project.render.midi(table_canon.simultaneous_event)
