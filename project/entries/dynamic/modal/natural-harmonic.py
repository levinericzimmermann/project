import fractions
import itertools
import operator
import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_events
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, pitch=None, **kwargs):
    try:
        assert context.modal_event.pitch is not None
        assert isinstance(context.modal_event, clock_events.ModalEvent1)
        orchestration = context.orchestration
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert isinstance(instrument, music_parameters.StringInstrumentMixin)
        pitch = pitch or get_pitch(context)
        assert instrument.get_harmonic_pitch_variant_tuple(pitch, tolerance=TOLERANCE)
        assert context.energy > 50
    except AssertionError:
        return False
    return True


def main(
    context,
    random,
    activity_level,
    double_harmonic_level: int = 8,
    pizzicato_level: int = 3,
    # Double harmonics are even more difficult to play
    # with pizzicato, therefore we use a factor in order
    # to reduce likelihood of pizzicato in case we have
    # a double harmonic.
    double_harmonic_pizzicato_factor: float = 0.5,
    min_harmonicity: float = 0.15,
    pitch=None,
    **kwargs,
) -> timeline_interfaces.EventPlacement:
    duration = context.modal_event.clock_event.duration

    if context.index % 4 == 3:
        position = 0.95
    else:
        position = 0.5

    real_duration = fractions.Fraction(27, 16)
    if real_duration > duration:
        real_duration = duration - fractions.Fraction(1, 16)
    start_range, end_range = project_utilities.get_ranges(
        real_duration, duration, position
    )

    orchestration = context.orchestration
    instrument = orchestration[0]
    scale = context.modal_event.scale
    pitch = pitch or get_pitch(context)
    pitch_tuple = instrument.get_harmonic_pitch_variant_tuple(
        pitch, tolerance=TOLERANCE
    )
    second_pitch_candidate_tuple = get_second_pitch_candidate_tuple(
        pitch,
        instrument,
        scale,
    )

    if real_duration > fractions.Fraction(25, 16):
        event_count_range = ranges.Range(2, 3)
    elif real_duration > fractions.Fraction(22, 16):
        event_count_range = ranges.Range(1, 3)
    else:
        event_count_range = ranges.Range(1, 2)

    event_count = random.choice(
        tuple(range(event_count_range.start, event_count_range.end + 1))
    )

    pitch_list_tuple, node_list_tuple = get_pitch_list_tuple_and_node_list_tuple(
        pitch_tuple,
        second_pitch_candidate_tuple,
        instrument,
        double_harmonic_level,
        min_harmonicity,
        random,
        activity_level,
        event_count,
    )

    sequential_event = core_events.SequentialEvent([])
    for i, pitch_list, node_list in zip(
        range(event_count), pitch_list_tuple, node_list_tuple
    ):
        if i != 0:
            r = music_events.NoteLike([], 0.5)
            sequential_event.append(r)

        note = music_events.NoteLike(pitch_list, 1, volume="ppp")
        nhnl = note.playing_indicator_collection.natural_harmonic_node_list
        nhnl.extend(node_list)
        # Parenthesize string indicator
        nhnl.parenthesize_lower_note_head = True
        add_pizzicato(
            note,
            pitch_list,
            pizzicato_level,
            double_harmonic_pizzicato_factor,
            node_list,
            activity_level,
        )
        sequential_event.append(note)

    simultaneous_event = project_events.SimultaneousEventWithRepetition(
        [
            project_events.TaggedSimultaneousEventWithRepetition(
                [sequential_event],
                tag=instrument.name,
            )
        ]
    )

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


def get_pitch_list_tuple_and_node_list_tuple(
    pitch_tuple,
    second_pitch_candidate_tuple,
    instrument,
    double_harmonic_level,
    min_harmonicity,
    random,
    activity_level,
    event_count,
):
    pitch_harmonic_tuple_list = [
        instrument.pitch_to_natural_harmonic_tuple(p, tolerance=TOLERANCE)
        for p in pitch_tuple
    ]

    second_pitch_harmonic_tuple_list = [
        instrument.pitch_to_natural_harmonic_tuple(p, tolerance=TOLERANCE)
        for p in second_pitch_candidate_tuple
    ]

    # If we have any double harmonic option and the activity level is
    # positive: let's make a double harmonic.
    if (
        valid_node_combination_list := get_valid_node_combination_list(
            pitch_harmonic_tuple_list, second_pitch_harmonic_tuple_list, min_harmonicity
        )
    ) and activity_level(double_harmonic_level):
        max_fitness = max(valid_node_combination_list, key=operator.itemgetter(0))[0]
        valid_node_combination_list = [
            valid_node_combination[1:]
            for valid_node_combination in valid_node_combination_list
            if valid_node_combination[0] == max_fitness
        ]
        node_list = random.choice(valid_node_combination_list)
        # Double harmonics are difficult to play, so we just repeat
        # the same double stop multiple times.
        node_list_tuple = tuple(node_list for _ in range(event_count))

    # Otherwise we play a single harmonic.
    else:
        node_list_tuple = get_single_pitch_node_list_tuple(
            pitch_harmonic_tuple_list, instrument, event_count, random
        )

    pitch_list_tuple = tuple(
        [n.natural_harmonic.pitch for n in node_list] for node_list in node_list_tuple
    )
    return pitch_list_tuple, node_list_tuple


def get_valid_node_combination_list(
    pitch_harmonic_tuple_list, second_pitch_harmonic_tuple_list, min_harmonicity
):
    valid_node_combination_list = []
    for h_tuple0, h_tuple1 in itertools.product(
        pitch_harmonic_tuple_list, second_pitch_harmonic_tuple_list
    ):
        for h0, h1 in itertools.product(h_tuple0, h_tuple1):
            # (1) Strings need to be neighbours (string players can only
            #     make fingerings with double harmonics if they are next
            #     to each other).
            if abs(h0.string.index - h1.string.index) != 1:
                continue
            # (2) They need to be harmonic!
            if (h0.pitch - h1.pitch).harmonicity_simplified_barlow < min_harmonicity:
                continue
            # (3) The nodes can't be too far from each other (too far to
            #     touch both), nor can they be equal (difficult fingering).
            for n0, n1 in itertools.product(h0.node_tuple, h1.node_tuple):
                interval_in_cents = abs((n0.interval - n1.interval).interval)
                fitness = DOUBLE_HARMONIC_DISTANCE_FITNESS_ENVELOPE.value_at(
                    interval_in_cents
                )
                if fitness > 0:
                    valid_node_combination_list.append((fitness, n0, n1))
    return valid_node_combination_list


def get_pitch(context):
    return context.modal_event.pitch


def get_second_pitch_candidate_tuple(pitch, instrument, scale):
    normalized_pitch = pitch.normalize(False)
    candidate_list = [
        # TODO(Replace with 'scale_degree_to_pitch_class'!)
        scale.scale_position_to_pitch((scale_degree, 0)).normalize(False)
        for scale_degree in range(scale.scale_degree_count)
    ]
    candidate_list = list(filter(lambda p: p != normalized_pitch, candidate_list))
    second_pitch_candidate_list = []
    for candidate in candidate_list:
        pitch_variant_tuple = instrument.get_harmonic_pitch_variant_tuple(
            candidate, tolerance=TOLERANCE
        )
        second_pitch_candidate_list.extend(pitch_variant_tuple)
    return tuple(second_pitch_candidate_list)


def get_single_pitch_node_list_tuple(
    pitch_harmonic_tuple_list, instrument, event_count, random
):
    # Inner choice picks octave, first [0] picks natural harmonic
    # node_tuple = pitch_harmonic_tuple_list[-1][0].node_tuple
    node_tuple = random.choice(pitch_harmonic_tuple_list)[0].node_tuple

    if event_count < 2:
        node_list = [node_tuple[0]]
        return tuple(node_list for _ in range(event_count))

    main_pitch = node_tuple[0].natural_harmonic.pitch

    valid_node_combination_list = []

    # Let's try to find at least one other harmonic, which
    # we can play & which is close to the harmonic which we already have:
    # close in terms of pitch distance, but also close in terms
    # of fingers.
    for second_pitch in instrument.harmonic_pitch_tuple:
        # Not the same pitch
        if second_pitch == main_pitch:
            continue

        # Close in terms of pitch
        if abs(second_pitch.get_pitch_interval(main_pitch).interval) >= MAX_MELODIC_DISTANCE_INTERVAL:
            continue

        natural_harmonic_tuple = instrument.pitch_to_natural_harmonic_tuple(
            second_pitch
        )
        for natural_harmonic in natural_harmonic_tuple:
            for n0, n1 in itertools.product(node_tuple, natural_harmonic.node_tuple):
                interval_in_cents = abs((n0.interval - n1.interval).interval)
                fitness = MELODIC_HARMONIC_DISTANCE_FITNESS_ENVELOPE.value_at(
                    interval_in_cents
                )
                if fitness > 0:
                    valid_node_combination_list.append((fitness, n0, n1))

    if not valid_node_combination_list:
        node_list = [node_tuple[0]]
        return tuple(node_list for _ in range(event_count))

    node_combination = sorted(valid_node_combination_list, key=lambda c: c[0])[-1]
    main_node, side_node = node_combination[1:]

    node_list_list = [[main_node] for _ in range(event_count)]
    node_list_list[-2] = [side_node]
    return tuple(node_list_list)


def add_pizzicato(
    note,
    pitch_list,
    pizzicato_level,
    double_harmonic_pizzicato_factor,
    node_list,
    activity_level,
):
    pizzicato_level = (
        int(pizzicato_level * double_harmonic_pizzicato_factor)
        if len(pitch_list) > 1
        else pizzicato_level
    )

    # Pizzicato with very high harmonics only create noisy
    # sounds, almost no pitch can be heard. So let's avoid
    # pizzicato for high harmonics.
    for node in node_list:
        if node.natural_harmonic.index > 4:
            pizzicato_level = 0
            break

    if activity_level(pizzicato_level):
        cpoint, duration_line = "pizzicato", False
    else:
        cpoint, duration_line = "ordinario", True

    note.notation_indicator_collection.duration_line.is_active = duration_line
    note.playing_indicator_collection.string_contact_point.contact_point = cpoint

MAX_MELODIC_DISTANCE_INTERVAL = 400

TOLERANCE = music_parameters.DirectPitchInterval(6)

# time = cents; value = fitness
DOUBLE_HARMONIC_DISTANCE_FITNESS_ENVELOPE = core_events.Envelope(
    # If 0 distance (so 3/2) it's difficult to intonate.
    # Around 200 cents is the easiest.
    # If too far it's difficult again
    [[0, 0], [10, 0], [200, 1], [400, 0]]
)

# time = cents; value = fitness
MELODIC_HARMONIC_DISTANCE_FITNESS_ENVELOPE = core_events.Envelope(
    [[0, 1], [10, 1], [200, 1], [450, 0]]
)
