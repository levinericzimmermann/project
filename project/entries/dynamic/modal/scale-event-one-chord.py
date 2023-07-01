import fractions
import functools
import itertools
import operator

from mutwo import clock_events
from mutwo import core_events
from mutwo import core_utilities
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert context.index % 4 in (2, 3)
        assert context.energy >= 40 and context.energy <= 50
        assert len(context.orchestration) == 3
        for instrument in context.orchestration:
            assert isinstance(instrument, music_parameters.abc.PitchedInstrument)
    except AssertionError:
        return False
    return True


def main(context, activity_level, **kwargs) -> timeline_interfaces.EventPlacement:
    orchestration = context.orchestration
    scale = context.modal_event.scale

    if isinstance(context.modal_event, clock_events.ModalEvent0):
        pitch = context.modal_event.end_pitch
    elif isinstance(context.modal_event, clock_events.ModalEvent1):
        pitch = context.modal_event.pitch
    else:
        raise NotImplementedError(
            "can't find pitch for modal event "
            f"{context.modal_event} of type {type(context.modal_event)}"
        )

    duration = context.modal_event.clock_event.duration

    real_duration = fractions.Fraction(26, 16)
    if real_duration > duration:
        real_duration = duration - fractions.Fraction(2, 16)
    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 1)

    instrument_to_pitch_lists = {}
    for instrument in orchestration:
        match instrument.name:
            case "v":
                pop = pop_cello
            case "harp":
                pop = pop_harp
            case _:
                pop = pop_generic
        instrument_to_pitch_lists[instrument.name] = pop(instrument, scale)

    instrument_to_pitch_list = get_instrument_to_pitch_list(
        instrument_to_pitch_lists, pitch
    )

    simultaneous_event = core_events.SimultaneousEvent([])
    d = fractions.Fraction(1, 1)
    for instrument in orchestration:
        tagged_simultaneous_event = core_events.TaggedSimultaneousEvent(
            [], tag=instrument.name
        )
        n = music_events.NoteLike(instrument_to_pitch_list[instrument.name], d, "pppp")
        n.notation_indicator_collection.duration_line.is_active = True
        seq = core_events.SequentialEvent([n])

        if instrument.name == "harp":
            upper_staff = core_events.SequentialEvent([music_events.NoteLike([], d)])
            upper_staff[0].notation_indicator_collection.clef.name = "treble"
            tagged_simultaneous_event.append(upper_staff)
            seq[0].notation_indicator_collection.clef.name = "bass"

        tagged_simultaneous_event.append(seq)
        simultaneous_event.append(tagged_simultaneous_event)

    add_synchronization_points(simultaneous_event)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


def pop_generic(instrument, scale):
    pitch_lists = []
    for pitch in scale.pitch_tuple:
        if pitch in instrument:
            pitch_lists.append([pitch])
    return tuple(pitch_lists)


def pop_harp(instrument, scale):
    pitch_lists = []
    for scale_index in range(scale.scale_degree_count):
        pitch_list = instrument.get_pitch_variant_tuple(
            scale.scale_position_to_pitch((scale_index, 0))
        )
        for pitch in pitch_list:
            if pitch in BOWED_HARP_AMBITUS:
                pitch_lists.append([pitch])
    return tuple(pitch_lists)


BOWED_HARP_AMBITUS = music_parameters.OctaveAmbitus(
    music_parameters.JustIntonationPitch("1/5"),
    music_parameters.JustIntonationPitch("2/5"),
)


def pop_cello(instrument, scale):
    pitch_lists = []
    for klang in instrument.v_klang_tuple:
        pitch_list = [klang.main_string_pitch, klang.side_string_pitch]
        if pitch_list[0] == pitch_list[1]:  # prohibit unisono
            continue
        if all([pitch in scale for pitch in pitch_list]):
            pitch_lists.append(pitch_list)
    return tuple(pitch_lists)


# convert potential to decision
def get_instrument_to_pitch_list(instrument_to_pitch_lists, reference_pitch):
    pitch_count = sum(
        [len(pitch_lists[0]) for pitch_lists in instrument_to_pitch_lists.values()]
    )
    min_pitch_class_count = PITCH_COUNT_TO_MIN_PITCH_CLASS_COUNT[pitch_count]
    instrument_tuple = tuple(instrument_to_pitch_lists.keys())
    pitch_list_tuple = tuple(
        instrument_to_pitch_lists[i] for i in instrument_to_pitch_lists.keys()
    )

    solution_list = []
    secondary_solution_list = []
    for combination in itertools.product(*pitch_list_tuple):
        pitch_list = functools.reduce(operator.add, combination)
        pitch_class_tuple = core_utilities.uniqify_sequence(
            [p.normalize(mutate=False) for p in pitch_list]
        )
        if len(pitch_class_tuple) >= min_pitch_class_count:
            if len(pitch_list) == core_utilities.uniqify_sequence(pitch_list):
                s = get_solution(
                    pitch_list, combination, instrument_tuple, reference_pitch
                )
                solution_list.append(s)
            else:
                s = get_solution(
                    pitch_list, combination, instrument_tuple, reference_pitch
                )
                secondary_solution_list.append(s)

    if not solution_list:
        solution_list = secondary_solution_list

    return max(solution_list, key=lambda s: s[1])[0]


def get_solution(pitch_list, combination, instrument_tuple, reference_pitch):
    fitness = sum(
        [
            (p0 - p1).harmonicity_simplified_barlow
            for p0, p1 in itertools.combinations(pitch_list + [reference_pitch], 2)
        ]
    )
    s = {i: pitch_list for i, pitch_list in zip(instrument_tuple, combination)}
    return (s, fitness)


PITCH_COUNT_TO_MIN_PITCH_CLASS_COUNT = (
    # pc  pitch
    0,  # 0
    1,  # 1
    2,  # 2
    2,  # 3
    3,  # 4
    3,  # 5
)


def add_synchronization_points(simultaneous_event):
    for sim in simultaneous_event[:-1]:
        seq = sim[-1]
        syn = seq[0].notation_indicator_collection.synchronization_point
        syn.length = 5
        syn.direction = False
