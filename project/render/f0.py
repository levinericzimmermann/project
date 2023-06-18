from mutwo import project_converters

e2f0 = project_converters.EventToF0()


def f0(simultaneous_event):
    bpath = "builds/f0/"
    for event in simultaneous_event:
        path = f"{bpath}/{event.tag}.f0"
        print(repr(e2f0(event)))
        with open(path, 'w') as f:
            f.write(e2f0(event))
