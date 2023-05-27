import ranges

from mutwo import common_generators
from mutwo import music_parameters


def is_supported(context, scale, dyad, **kwargs):
    try:
        assert len(context.orchestration) == 1
        assert isinstance(context_to_instrument(context), music_parameters.CelticHarp)
        assert context.modal_event.start_pitch is not None
        assert context.modal_event.end_pitch is not None
        assert context.index % 3 != 0
    except AssertionError:
        return False
    return scale.is_supported(context, **kwargs) and dyad.is_supported(
        context, **kwargs
    )


def main(
    context, scale, dyad, activity_level, random, direction=None, **kwargs
) -> tuple[tuple[music_parameters.abc.Pitch, ...], ...]:
    if direction is None:
        direction = activity_level(5)

    if direction:
        distance_range0, distance_range1 = DISTANCE_RANGE_TUPLE
    else:
        distance_range1, distance_range0 = DISTANCE_RANGE_TUPLE

    octave_count = 0
    pitch_tuple = tuple([])
    # Ensure we don't have a too short scale object!
    while len(pitch_tuple) < 3 and octave_count < 3:
        pitch_tuple = scale(
            context, direction=direction, octave_count=octave_count, **kwargs
        )
        octave_count += 1

    instrument = context_to_instrument(context)

    pitch_list_list = [[p] for p in pitch_tuple]
    if activity_level(6):
        add_dyad(
            context,
            pitch_list_list,
            0,
            dyad,
            distance_range=distance_range0,
        )
    if activity_level(7):
        # We want to add an inversion of our ending dyad in
        # case the last step is a second, because otherwise it
        # sounds too much like a cadenca / the end of a part.
        inversion = (
            abs(
                pitch_list_list[-1][0]
                .get_pitch_interval(pitch_list_list[-2][0])
                .interval
            )
            < 250
        )
        add_dyad(
            context,
            pitch_list_list,
            -1,
            dyad,
            distance_range=distance_range1,
            prohibited_pitch_list=pitch_list_list[0],
        )
        if inversion:
            add_inversion(instrument, pitch_list_list)

    # add_octave_parallel(pitch_list_list, activity_level)

    add_inverse_movement(
        pitch_list_list, activity_level, scale, direction, context, kwargs, instrument
    )

    # TODO: Consider to remove some pitches in order
    # to gain an easier fingering. Or to make some of them
    # optional?
    ...
    return tuple(tuple(pl) for pl in pitch_list_list)


def add_dyad(
    context,
    pitch_list_list,
    index,
    dyad,
    distance_range=ranges.Range(4, 7),
    prohibited_pitch_list=[],
):
    pitch_list_list[index] = dyad(
        context,
        pitch=pitch_list_list[index][0],
        direction=False,
        distance_range=distance_range,
        prohibited_pitch_list=prohibited_pitch_list,
    )


DISTANCE_RANGE_TUPLE = (ranges.Range(3, 5), ranges.Range(6, 9))


def add_inversion(instrument, pitch_list_list):
    dyad = pitch_list_list[-1]
    oct0, oct1 = (p.octave for p in dyad)
    inversion = list(p.register(o, mutate=False) for o, p in zip((oct1, oct0), dyad))
    if all(p in instrument for p in inversion):
        pitch_list_list.append(inversion)


def add_octave_parallel(pitch_list_list, activity_level):
    # TODO(Ensure we don't use pitches outside the harps range)
    if all([len(pl) <= 1 for pl in pitch_list_list]) and activity_level(4):
        for pl in pitch_list_list:
            if pl:
                p = pl[0]
                pl.append(p - music_parameters.JustIntonationPitch("2/1"))


def add_inverse_movement(
    pitch_list_list, activity_level, scale, direction, context, kwargs, instrument
):
    if all([len(pl) <= 1 for pl in pitch_list_list]) and activity_level(4):
        event_count = len(pitch_list_list)
        octave_count = 0
        inverse_scale = []
        while len(inverse_scale) < event_count:
            previous_inverse_scale = inverse_scale
            inverse_scale = scale(
                context, direction=not direction, octave_count=octave_count, **kwargs
            )
            octave_count += 1

        inverse_scale = previous_inverse_scale

        if (difference := event_count - len(inverse_scale)) < 0:
            end = inverse_scale[-1]
            remove_cycle = common_generators.euclidean(
                len(inverse_scale) - 1, event_count - 1
            )
            adjusted_inverse_scale = []
            for p, is_alive in zip(inverse_scale, remove_cycle):
                if is_alive:
                    adjusted_inverse_scale.append(p)
            adjusted_inverse_scale.append(end)

            inverse_scale = adjusted_inverse_scale

        else:
            inverse_scale = list(inverse_scale)
            for _ in range(difference):
                inverse_scale.insert(0, None)

        for p, pl in zip(inverse_scale, pitch_list_list):
            if p:
                p = p - music_parameters.JustIntonationPitch("2/1")
                if p not in pl:
                    pl.append(p)

        if len(pitch_list_list[-1]) > 1:
            return
        last_pitch = pitch_list_list[-1][0]
        fifth = last_pitch - music_parameters.JustIntonationPitch("3/2")
        fourth = last_pitch - music_parameters.JustIntonationPitch("4/3")
        octave = last_pitch - music_parameters.JustIntonationPitch("2/1")
        if octave in instrument:
            added = octave
        elif fifth in instrument:
            added = fifth
        elif fourth in instrument:
            added = fourth
        else:
            return
        if added != p:  # no pitch repetition
            pitch_list_list[-1].append(added)


def context_to_instrument(context):
    orchestration = context.orchestration
    return orchestration[0]
