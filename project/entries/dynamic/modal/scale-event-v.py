import quicktions as fractions
import itertools
import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import diary_interfaces
from mutwo import music_events
from mutwo import project_parameters
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert isinstance(context, diary_interfaces.ModalContext0)
        assert context.modal_event.start_pitch is not None
        assert context.modal_event.end_pitch is not None
        assert isinstance(context_to_instrument(context), project_parameters.V)
        assert context.modal_event.start_pitch != context.modal_event.end_pitch
        assert context.index % 3 == 0
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

    real_duration = fractions.Fraction(37, 16)
    if real_duration > duration:
        real_duration = duration - fractions.Fraction(2, 16)

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

    scale = modal_event_to_convert.scale
    klang_list = get_klang_list(
        modal_event_to_convert, scale, instrument, real_duration
    )
    sequential_event = make_sequential_event(
        klang_list, random, instrument, activity_level
    )
    v_event = core_events.TaggedSimultaneousEvent([sequential_event], tag=tag)

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
            # if instrument.v_klang_tuple[i].main_string_pitch in scale.pitch_tuple
        ]
        if klang_list[0].side_string_pitch not in [
            s.tuning for s in instrument.string_tuple
        ]:
            continue
        klang_interpolation_list.append(tuple(klang_list))

    event_count = duration_to_event_count(duration)
    klang_count_tuple = tuple(len(k) for k in klang_interpolation_list)
    difference_tuple = tuple(abs(event_count - kc) for kc in klang_count_tuple)

    # best_klang_interpolations = [klang_interpolation_list[i] for i, d in enumerate(difference_tuple) if i == min(difference_tuple)]
    klang_list = klang_interpolation_list[difference_tuple.index(min(difference_tuple))]

    return klang_list


def make_sequential_event(klang_list, random, instrument, activity_level):
    sequential_event = core_events.SequentialEvent(
        [
            music_events.NoteLike(
                [klang.main_string_pitch, klang.side_string_pitch],
                random.choice([1.75, 2.0, 2.5]),
                "mf",
            )
            for klang in klang_list
        ]
    )
    sequential_event[-1].duration = 4

    for n in sequential_event:
        n.playing_indicator_collection.string_contact_point.contact_point = "ordinario"

    n0_n = sequential_event[0].notation_indicator_collection
    n0_n.markup.content = '"arco mobile"'
    n0_n.markup.direction = "up"

    # Order matters!
    add_pizzicato(sequential_event, klang_list, instrument)
    remove_side_pitch(sequential_event, klang_list, activity_level)
    # add_arpeggio(sequential_event, klang_list, activity_level)
    add_bend_after(sequential_event)

    started_with_empty_string = start_with_empty_string(
        sequential_event, instrument, klang_list
    )

    for i, n in enumerate(sequential_event):
        if i == 0 and started_with_empty_string:
            continue
        if (
            n.playing_indicator_collection.string_contact_point.contact_point != "pizzicato"
            and n.playing_indicator_collection.bend_after.bend_amount is None
        ):
            n.notation_indicator_collection.duration_line.is_active = True

    return sequential_event


def start_with_empty_string(sequential_event, instrument, klang_list):
    if klang_list[0].side_string_pitch in [s.tuning for s in instrument.string_tuple]:
        sequential_event[0].duration *= 1.5
        sequential_event.split_child_at(sequential_event[0].duration / 2)
        n_empty_string = sequential_event[0]
        n_empty_string.pitch_list = [klang_list[0].side_string_pitch]
        n_empty_string.playing_indicator_collection.tie.is_active = True
        # Hardcode empty string duration:
        # Tie only works if duration doesn't need to be split, because
        # otherwise 'mutwo.abjad' adds 's' inbetween and Lilypond
        # won't tie over 'Skips'.
        n_empty_string.duration = fractions.Fraction(2, 1)
        sequential_event[1].playing_indicator_collection.arpeggio.direction = None


def add_arpeggio(sequential_event, klang_list, activity_level):
    for n, klang in zip(sequential_event, klang_list):
        if len(n.pitch_list) < 2:
            continue
        if sum(klang.main_string_pitch.exponent_tuple[2:]) == 0 and activity_level(6):
            n.playing_indicator_collection.arpeggio.direction = (
                "up" if klang.main_string_pitch > klang.side_string_pitch else "down"
            )


def add_pizzicato(sequential_event, klang_list, instrument):
    for n, klang in zip(sequential_event, klang_list):
        if klang_list[0].main_string_pitch in [
            s.tuning for s in instrument.string_tuple
        ]:
            n.pitch_list = klang_list[0].main_string_pitch
            n.playing_indicator_collection.string_contact_point.contact_point = "pizzicato"


def add_bend_after(sequential_event):
    # If two pitches repeat, the second pitch should do something different: a
    # glissando seems to be suitable.
    for n0, n1, n2 in zip(sequential_event, sequential_event[1:], sequential_event[2:]):
        if n1.playing_indicator_collection.string_contact_point.contact_point == "pizzicato":
            continue
        if len(n1.pitch_list) == 1 and n1.pitch_list[0] in n0.pitch_list:
            # If next pitch goes higher, we go down, and upside down.
            bend_amount = 1.5
            if any([p > n1.pitch_list[0] for p in n2.pitch_list]):
                bend_amount *= -1
            n1.playing_indicator_collection.bend_after.bend_amount = bend_amount
            n1.playing_indicator_collection.bend_after.minimum_length = 5


def remove_side_pitch(sequential_event, klang_list, activity_level):
    for n, klang in zip(sequential_event[1:], klang_list[1:]):
        if len(n.pitch_list) < 2:
            continue
        if sum(klang.main_string_pitch.exponent_tuple[2:]) == 0 and activity_level(4):
            n.pitch_list = klang.main_string_pitch


def range_(start, end):
    if end < start:
        return reversed(tuple(range(end, start + 1)))
    return range(start, end + 1)


def duration_to_event_count(duration):
    return int(duration / density[0]) * density[1]


# For 7 seconds 1 attack
density = (fractions.Fraction(9, 16), 1)
