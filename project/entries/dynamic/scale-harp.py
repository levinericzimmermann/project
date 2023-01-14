import ranges

from mutwo import music_parameters


def is_supported(context, scale, dyad, **kwargs):
    try:
        orchestration = context.orchestration
        instrument = orchestration[0]
        assert isinstance(instrument, music_parameters.CelticHarp)
    except AssertionError:
        return False
    return scale.is_supported(context, **kwargs) and dyad.is_supported(
        context, **kwargs
    )


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
        add_dyad(
            context,
            pitch_list_list,
            -1,
            dyad,
            distance_range=distance_range1,
            prohibited_pitch_list=pitch_list_list[0],
        )
    # TODO: Consider to remove some pitches in order
    # to gain an easier fingering. Or some of them optional?
    ...
    return tuple(tuple(pl) for pl in pitch_list_list)
