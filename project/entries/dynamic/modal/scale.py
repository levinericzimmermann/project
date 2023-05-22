import ranges

from mutwo import clock_events
from mutwo import music_parameters


def get_start_pitch_class_and_end_pitch_class(
    context, start_pitch=None, end_pitch=None
):
    modal_event_to_convert = context.modal_event
    start_pitch = start_pitch or modal_event_to_convert.start_pitch
    end_pitch = end_pitch or modal_event_to_convert.end_pitch

    return start_pitch, end_pitch


def is_supported(context, start_pitch=None, end_pitch=None, **kwargs):
    orchestration = context.orchestration
    try:
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert instrument.is_pitched
        assert isinstance(context.modal_event, clock_events.ModalEvent0)
        start_pitch, end_pitch = get_start_pitch_class_and_end_pitch_class(
            context, start_pitch, end_pitch
        )
        assert start_pitch != end_pitch
    except AssertionError:
        return False
    return True


def get_start_pitch_and_end_pitch(
    start_pitch_class, end_pitch_class, instrument, direction, octave_count
):
    start_pitch_tuple, end_pitch_tuple = (
        instrument.pitch_ambitus.get_pitch_variant_tuple(p)
        for p in (start_pitch_class, end_pitch_class)
    )

    # Depending on direction, octave_count and start_pitch_tuple +
    # end_pitch_tuple, we can only pick certain start-pitch /
    # end-pitch combinations.
    first_start_pitch, first_end_pitch = start_pitch_tuple[0], end_pitch_tuple[0]
    if first_start_pitch > first_end_pitch:
        if direction is True:  # rise
            end_pitch_tuple = end_pitch_tuple[1:]
    elif direction is False:  # and first_start_pitch < first_end_pitch
        start_pitch_tuple = start_pitch_tuple[1:]

    pitch_pair_tuple = tuple(zip(start_pitch_tuple, end_pitch_tuple))
    octave_count += 1
    if (pitch_pair_count := len(pitch_pair_tuple)) < octave_count:
        octave_count = pitch_pair_count
    remainder = pitch_pair_count - octave_count
    remainder_left = int(remainder / 2)
    remainder_right = remainder - remainder_left

    if remainder_right:
        pitch_pair_tuple = pitch_pair_tuple[remainder_left:-remainder_right]
    else:
        pitch_pair_tuple = pitch_pair_tuple[remainder_left:]

    if not pitch_pair_tuple:
        return None

    if direction:
        start_pitch = pitch_pair_tuple[0][0]
        end_pitch = pitch_pair_tuple[-1][1]
    else:
        start_pitch = pitch_pair_tuple[-1][0]
        end_pitch = pitch_pair_tuple[0][1]

    return start_pitch, end_pitch


def main(
    context,
    random,
    start_pitch=None,
    end_pitch=None,
    octave_count=0,
    # True: rise, False: fall
    direction: bool = True,
    **kwargs,
) -> tuple[music_parameters.abc.Pitch, ...]:

    modal_event_to_convert = context.modal_event
    start_pitch_class, end_pitch_class = get_start_pitch_class_and_end_pitch_class(
        context, start_pitch, end_pitch
    )

    scale = modal_event_to_convert.scale
    orchestration = context.orchestration
    instrument = orchestration[0]

    start_pitch_and_end_pitch = get_start_pitch_and_end_pitch(
        start_pitch_class, end_pitch_class, instrument, direction, octave_count
    )
    if not start_pitch_and_end_pitch:
        return tuple([])

    start_pitch, end_pitch = start_pitch_and_end_pitch

    def range_(start, end):
        if end < start:
            return reversed(tuple(range(end, start + 1)))
        return range(start, end + 1)

    start_index, end_index = (
        scale.pitch_to_scale_index(pitch) for pitch in (start_pitch, end_pitch)
    )
    pitch_list = []
    for pitch_index in range_(start_index, end_index):
        if (new_pitch := scale.scale_index_to_pitch(pitch_index)) in instrument:
            pitch_list.append(new_pitch)
    return tuple(pitch_list)
