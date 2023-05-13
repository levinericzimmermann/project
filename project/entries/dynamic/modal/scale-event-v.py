import quicktions as fractions
import itertools
import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import project_parameters
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert isinstance(context_to_instrument(context), project_parameters.V)
    except AssertionError:
        return False
    return True


def main(
    context, random, activity_level, **kwargs
) -> timeline_interfaces.EventPlacement:
    modal_event_to_convert = context.modal_event
    instrument = context.orchestration[0]
    tag = instrument.name
    duration = modal_event_to_convert.clock_event.duration

    start_percentage = 0.1
    # start_percentage = random.uniform(0.1, 0.3)
    end_percentage = 0.885
    # end_percentage = random.uniform(0.8, 0.92)

    real_duration = (duration * end_percentage) - (duration * start_percentage)

    scale = modal_event_to_convert.scale
    klang_list = get_klang_list(
        modal_event_to_convert, scale, instrument, real_duration
    )
    sequential_event = make_sequential_event(klang_list, random, instrument)
    v_event = core_events.TaggedSimultaneousEvent([sequential_event], tag=tag)

    start_range = ranges.Range(
        duration * (start_percentage * 0.95), duration * start_percentage
    )
    end_range = ranges.Range(
        duration * (end_percentage * 0.95), duration * end_percentage
    )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([v_event]), start_range, end_range
    ).move_by(context.start)


def context_to_instrument(context):
    orchestration = context.orchestration
    return orchestration[0]


def scale_degree_to_v_klang_tuple(scale_degree: int, instrument):
    allowed_klang_list = []
    for klang in instrument.v_klang_tuple:
        if klang.scale_degree == scale_degree:
            allowed_klang_list.append(klang)
    return tuple(allowed_klang_list)


def get_klang_list(modal_event_to_convert, scale, instrument, duration):
    start_pitch = modal_event_to_convert.start_pitch
    end_pitch = modal_event_to_convert.end_pitch

    start_pitch_degree, end_pitch_degree = (
        scale.pitch_to_scale_position(p)[0] for p in (start_pitch, end_pitch)
    )

    start_klang_tuple, end_klang_tuple = (
        scale_degree_to_v_klang_tuple(d, instrument)
        for d in (start_pitch_degree, end_pitch_degree)
    )

    klang_interpolation_list = []
    for start_klang, end_klang in itertools.product(start_klang_tuple, end_klang_tuple):
        start_klang_index, end_klang_index = (
            instrument.v_klang_tuple.index(k) for k in (start_klang, end_klang)
        )
        klang_list = [
            instrument.v_klang_tuple[i]
            for i in range_(start_klang_index, end_klang_index)
        ]
        klang_interpolation_list.append(tuple(klang_list))

    event_count = duration_to_event_count(duration)
    klang_count_tuple = tuple(len(k) for k in klang_interpolation_list)
    difference_tuple = tuple(abs(event_count - kc) for kc in klang_count_tuple)
    klang_list = klang_interpolation_list[difference_tuple.index(min(difference_tuple))]

    return klang_list


def make_sequential_event(klang_list, random, instrument):
    sequential_event = core_events.SequentialEvent(
        [
            music_events.NoteLike(
                [klang.main_string_pitch, klang.side_string_pitch],
                random.choice([1.0, 1.5, 2.0, 2.5]),
                "pp",
            )
            for klang in klang_list
        ]
    )
    sequential_event[-1].duration = 3

    started_with_empty_string = start_with_empty_string(sequential_event, instrument, klang_list)

    for i, n in enumerate(sequential_event):
        if i == 0 and started_with_empty_string:
            continue
        n.notation_indicator_collection.duration_line.is_active = True

    return sequential_event


def start_with_empty_string(sequential_event, instrument, klang_list):
    if klang_list[0].side_string_pitch in [s.tuning for s in instrument.string_tuple]:
        sequential_event[0].duration *= 1.5
        sequential_event.split_child_at(sequential_event[0].duration / 2)
        n_empty_string = sequential_event[0]
        n_empty_string.pitch_list = [klang_list[0].side_string_pitch]
        n_empty_string.playing_indicator_collection.tie.is_active = True
        # Tie only works if duration isn't too long, because
        # otherwise 'mutwo.abjad' adds 's' inbetween and Lilypond
        # won't tie over 'Skips'.
        n_empty_string.duration = fractions.Fraction(1, 1)


def range_(start, end):
    if end < start:
        return reversed(tuple(range(end, start + 1)))
    return range(start, end + 1)


def duration_to_event_count(duration):
    return int(duration / density[0]) * density[1]


# For 7 seconds 1 attack
density = (fractions.Fraction(7, 16), 1)
