import itertools
import operator
import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_events
from mutwo import timeline_interfaces


def is_supported(context, pitch=None, **kwargs):
    try:
        assert isinstance(context.modal_event, clock_events.ModalEvent1)
        orchestration = context.orchestration
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert isinstance(instrument, music_parameters.StringInstrumentMixin)
        pitch = pitch or get_pitch(context)
        assert instrument.get_harmonic_pitch_variant_tuple(pitch, tolerance=TOLERANCE)
    except AssertionError:
        return False
    return True


def main(
    context,
    random,
    activity_level,
    double_harmonic_level: int = 6,
    pizzicato_level: int = 10,
    # Double harmonics are even more difficult to play
    # with pizzicato, therefore we use a factor in order
    # to reduce likelihood of pizzicato in case we have
    # a double harmonic.
    double_harmonic_pizzicato_factor: float = 0.5,
    min_harmonicity: float = 0.15,
    pitch=None,
    **kwargs
) -> timeline_interfaces.EventPlacement:
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

    pitch_list, node_list = get_pitch_list_and_node_list(
        pitch_tuple,
        second_pitch_candidate_tuple,
        instrument,
        double_harmonic_level,
        min_harmonicity,
        random,
        activity_level,
    )

    note = music_events.NoteLike(pitch_list, 1, volume="pp")
    nhnl = note.playing_indicator_collection.natural_harmonic_node_list
    nhnl.extend(node_list)
    nhnl.parenthesize_lower_note_head = True  # Parenthesize string indicator

    simultaneous_event = project_events.SimultaneousEventWithRepetition(
        [
            project_events.TaggedSimultaneousEventWithRepetition(
                [core_events.SequentialEvent([note])],
                tag=instrument.name,
            )
        ]
    )

    pizzicato_level = (
        int(pizzicato_level * double_harmonic_pizzicato_factor)
        if len(pitch_list) > 1
        else pizzicato_level
    )

    for node in node_list:
        if node.natural_harmonic.index > 4:
            pizzicato_level = 0
            break

    if activity_level(pizzicato_level):
        cpoint = "pizzicato"
        repetition_count_range = ranges.Range(3, 6)
        simultaneous_event.repetition_count_range = repetition_count_range
        simultaneous_event[0].repetition_count_range = repetition_count_range
    else:
        cpoint = "ordinario"
        note.notation_indicator_collection.duration_line.is_active = True

    note.playing_indicator_collection.string_contact_point.contact_point = cpoint

    duration = context.modal_event.clock_event.duration
    start_range = ranges.Range(duration * 0.05, duration * 0.1)
    end_range = ranges.Range(duration * 0.95, duration * 0.985)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


def get_pitch_list_and_node_list(
    pitch_tuple,
    second_pitch_candidate_tuple,
    instrument,
    double_harmonic_level,
    min_harmonicity,
    random,
    activity_level,
):
    pitch_harmonic_tuple_list = [
        instrument.pitch_to_natural_harmonic_tuple(p, tolerance=TOLERANCE)
        for p in pitch_tuple
    ]

    second_pitch_harmonic_tuple_list = [
        instrument.pitch_to_natural_harmonic_tuple(p, tolerance=TOLERANCE)
        for p in second_pitch_candidate_tuple
    ]

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

    if valid_node_combination_list and activity_level(double_harmonic_level):
        max_fitness = max(valid_node_combination_list, key=operator.itemgetter(0))[0]
        valid_node_combination_list = [
            valid_node_combination[1:]
            for valid_node_combination in valid_node_combination_list
            if valid_node_combination[0] == max_fitness
        ]
        node_list = random.choice(valid_node_combination_list)
    else:
        node_list = [
            # Inner choice picks octave, first [0] picks natural harmonic
            random.choice(pitch_harmonic_tuple_list)[0].node_tuple[0]
        ]

    pitch_list = [n.natural_harmonic.pitch for n in node_list]
    return pitch_list, node_list


def get_pitch(context):
    return context.modal_event.pitch


def get_second_pitch_candidate_tuple(pitch, instrument, scale):
    normalized_pitch = pitch.normalize(False)
    # TODO(Replace with scale.scale_degree_count, once implemented)
    scale_degree_count = len(set(scale.scale_degree_tuple))
    candidate_list = [
        # TODO(Replace with 'scale_degree_to_pitch_class'!)
        scale.scale_position_to_pitch((scale_degree, 0)).normalize(False)
        for scale_degree in range(scale_degree_count)
    ]
    candidate_list = list(filter(lambda p: p != normalized_pitch, candidate_list))
    second_pitch_candidate_list = []
    for candidate in candidate_list:
        pitch_variant_tuple = instrument.get_harmonic_pitch_variant_tuple(
            candidate, tolerance=TOLERANCE
        )
        second_pitch_candidate_list.extend(pitch_variant_tuple)
    return tuple(second_pitch_candidate_list)


TOLERANCE = music_parameters.DirectPitchInterval(6)

# time = cents; value = fitness
DOUBLE_HARMONIC_DISTANCE_FITNESS_ENVELOPE = core_events.Envelope(
    [[0, 0], [10, 0], [200, 1], [400, 0]]
)
