import os

from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_converters

e2f0 = project_converters.EventToF0()


def f0(simultaneous_event, index):
    simultaneous_event = simultaneous_event.copy()
    simultaneous_event.slide_in(
        0, core_events.SimpleEvent(20).set_parameter("r", False)
    )

    f_simultaneous_event = core_events.SimultaneousEvent(
        filter(
            lambda e: e.tag in TAG_TUPLE,
            simultaneous_event,
        )
    )
    # Ensure our event is always sorted in the same way!
    f_simultaneous_event.sort(key=lambda e: TAG_TUPLE.index(e.tag))

    if index not in (0, 6):
        assert len(f_simultaneous_event) == VOICE_COUNT

    if not f_simultaneous_event:
        return

    dclock = distribute_clock(simultaneous_event)

    bpath = f"builds/f0/day_{index + 1}_voice_"

    for voice_index, ambitus, event, metronome in zip(
        range(VOICE_COUNT), AMBITUS_TUPLE, f_simultaneous_event, dclock
    ):
        dir_path = f"{bpath}{voice_index}"

        for i, e in enumerate(event[0]):
            # 'event.r == False' is our initial offset event, don't touch
            # this.
            if not getattr(e, "r", True):
                continue

            if is_rest(e):
                # The volume of the noise part highly depends on the context.
                #
                #   (1) for the generalpause -36.5 DB is definitely too loud.
                #       -38 or something else in between was better => during
                #       the generalpause this noise should connect with the
                #       given atmospheric noise.
                #
                #   (2) but for noise during other pitched sounds, -36.85 wasn't
                #       that bad, but only for long noise parts.
                #
                #   (3) for short noise parts during other events -38 is ok.
                if e.duration > 10:
                    volume = music_parameters.DecibelVolume(-37.85)
                else:
                    volume = music_parameters.DecibelVolume(-38)

                event[0][i] = music_events.NoteLike(
                    music_parameters.DirectPitch(-1),
                    e.duration,
                    volume,
                )

            else:
                e.pitch_list[0] = ambitus.get_pitch_variant_tuple(e.pitch_list[0])[0]

        # Safety check, is everything correct?
        assert float(metronome.duration) == float(
            event.duration
        ), f"{float(metronome.duration)}, {float(event.duration)}"

        print(voice_index, " = ", event.tag, ",", dir_path)
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass
        n_path = f"{dir_path}/n.f0"
        p_path = f"{dir_path}/p.f0"
        for p, e, driver in (
            (n_path, event, project_converters.F0Driver.CONTINOUS),
            (p_path, metronome, project_converters.F0Driver.PERCUSSIVE),
        ):
            with open(p, "w") as f:
                f.write(e2f0(e, driver=driver))


# The rhythmic orientation ('metronome') is distributed on 3 different arduino.
# Each arduino therefore doesn't only give pitch/intonation orientation, but
# also rhythmic orientation.
def distribute_clock(simultaneous_event):
    dclock = core_events.SimultaneousEvent(
        [core_events.SequentialEvent([]) for _ in range(VOICE_COUNT)]
    )
    pclock = simultaneous_event["pclock"][0].tie_by(
        lambda e0, e1: is_rest(e1), mutate=False
    )
    for i, e in enumerate(pclock):

        if i != 0:
            assert not is_rest(e)

        add_index = i % VOICE_COUNT
        for i2, seq in enumerate(dclock):
            if not is_rest(e) and i2 == add_index:
                seq.append(
                    e.set_parameter(
                        "pitch_list", [METRONOME_PITCH_TUPLE[i2]], mutate=False
                    )
                )
            else:
                seq.append(core_events.SimpleEvent(e.duration))

    # Safety checks, is everything correct?
    tone_count = 0
    duration = dclock.duration

    for seq in dclock:
        seq.tie_by(lambda e0, e1: is_rest(e1))

        assert seq.duration == duration

        tone_count += len(list(filter(lambda e: not is_rest(e), seq)))

    assert tone_count == len(list(filter(lambda e: not is_rest(e), pclock)))

    return dclock


def is_rest(e):
    return not getattr(e, "pitch_list", [])


TAG_TUPLE = ("tonic", "partner", "written_instable_pitch")
j = music_parameters.JustIntonationPitch
METRONOME_PITCH_TUPLE = (j("1/2"), j("1/1"), j("2/1"))
AMBITUS_TUPLE = (
    music_parameters.OctaveAmbitus(j("3/4"), j("3/2")),
    music_parameters.OctaveAmbitus(j("15/16"), j("15/8")),
    music_parameters.OctaveAmbitus(j("16/15"), j("32/15")),
)
VOICE_COUNT = 3

assert len(TAG_TUPLE) == VOICE_COUNT
assert len(METRONOME_PITCH_TUPLE) == VOICE_COUNT
