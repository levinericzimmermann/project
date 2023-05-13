import ranges

from mutwo import music_parameters


def is_supported(context, scale, dyad, **kwargs):
    try:
        assert isinstance(context_to_instrument(context), music_parameters.CelticHarp)
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
            add_inversion(context, pitch_list_list)

    add_octave_parallel(pitch_list_list, activity_level)

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


def add_inversion(context, pitch_list_list):
    dyad = pitch_list_list[-1]
    oct0, oct1 = (p.octave for p in dyad)
    inversion = list(p.register(o, mutate=False) for o, p in zip((oct1, oct0), dyad))
    instrument = context_to_instrument(context)
    if all(p in instrument for p in inversion):
        pitch_list_list.append(inversion)


def add_octave_parallel(pitch_list_list, activity_level):
    # TODO(Ensure we don't use pitches outside the harps range)
    if all([len(pl) <= 1 for pl in pitch_list_list]) and activity_level(4):
        for pl in pitch_list_list:
            if pl:
                p = pl[0]
                pl.append(p - music_parameters.JustIntonationPitch("2/1"))


def context_to_instrument(context):
    orchestration = context.orchestration
    return orchestration[0]
