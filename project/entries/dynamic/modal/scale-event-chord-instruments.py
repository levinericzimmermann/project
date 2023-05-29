import operator

import quicktions as fractions

from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, alternating_scale_chords, **kwargs):
    try:
        orchestration = context.orchestration
        assert len(orchestration) > 1
        for i in orchestration:
            assert isinstance(i, music_parameters.abc.PitchedInstrument)
        assert context.index % 2 == 0
        assert context.index != 0
        assert context.energy > 50
    except AssertionError:
        return False
    return alternating_scale_chords.is_supported(context, **kwargs)


def main(context, alternating_scale_chords, random, **kwargs):
    chord_tuple = alternating_scale_chords(context, **kwargs)

    modal_event_to_convert = context.modal_event
    duration = modal_event_to_convert.clock_event.duration

    real_duration = fractions.Fraction(37, 16)
    if real_duration > duration:
        real_duration = duration - fractions.Fraction(2, 16)

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.3)

    simultaneous_event = core_events.SimultaneousEvent(
        [
            core_events.TaggedSimultaneousEvent(
                [core_events.SequentialEvent([])], tag=instrument.name
            )
            for instrument in context.orchestration
        ]
    )

    max_chord_index = len(chord_tuple) - 1

    for chord_index, chord in enumerate(chord_tuple):
        duration = random.choice([1, 1.5, 0.75])
        distribute_chord(
            duration,
            chord,
            simultaneous_event,
            context.orchestration,
            random,
            chord_index,
            max_chord_index,
        )

    for tagged_simultaneous_event in simultaneous_event[:-1]:
        sequential_event = tagged_simultaneous_event[0]
        i = 0
        n = sequential_event[i]
        while not hasattr(n, "pitch_list") or not n.pitch_list:
            i += 1
            try:
                n = sequential_event[i]
            except IndexError:
                n = None
        if n:
            n.notation_indicator_collection.synchronization_point.length = 5
            n.notation_indicator_collection.synchronization_point.direction = False

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


def distribute_chord(
    duration,
    chord,
    simultaneous_event,
    orchestration,
    random,
    chord_index,
    max_chord_index,
):
    pitch_count_dict = {p.normalize().exponent_tuple: 0 for p in chord}
    for instrument in orchestration:
        match instrument.name:
            case "v":
                pop = pop_cello
            case "harp":
                pop = pop_harp
            case _:
                pop = pop_generic
        pop(
            chord,
            pitch_count_dict,
            duration,
            simultaneous_event[instrument.name],
            instrument,
            random,
            chord_index,
            max_chord_index,
        )


def pop_cello(
    pitch_set,
    pitch_count_dict,
    duration,
    simultaneous_event,
    instrument,
    random,
    chord_index,
    max_chord_index,
):
    if not simultaneous_event:
        simultaneous_event.append(core_events.SequentialEvent())

    OPEN, FLAGEOLET, PYTHAGOREAN = 0, 1, 2

    possible_pitch_list = []
    for pitch in pitch_set:
        # On a cello we can either play:
        #
        #   (a) open strings
        for string in instrument.string_tuple:
            if string.tuning.exponent_tuple[1:] == pitch.exponent_tuple[1:]:
                possible_pitch_list.append((string.tuning, OPEN))

        #   (b) flageolets
        for v in instrument.get_harmonic_pitch_variant_tuple(
            pitch, tolerance=TOLERANCE
        ):
            possible_pitch_list.append((v, FLAGEOLET))

        #   (c) pythagorean intervals
        #       We avoid other microtonal pitches (difficult to intonate).
        if sum(pitch.exponent_tuple[2:]) == 0:
            for v in instrument.get_pitch_variant_tuple(pitch):
                possible_pitch_list.append((v, PYTHAGOREAN))

    if not possible_pitch_list:
        add_rest(simultaneous_event, duration)
        return

    pitch, pitchtype = sorted(possible_pitch_list, key=operator.itemgetter(1))[0]
    pitch_count_dict[pitch.normalize(mutate=False).exponent_tuple] += 1

    note = music_events.NoteLike(pitch, duration=duration, volume="pp")
    contact_point = "pizzicato"
    if pitchtype == FLAGEOLET:
        natural_harmonic = instrument.pitch_to_natural_harmonic_tuple(pitch)[0]
        node = natural_harmonic.node_tuple[0]
        note.playing_indicator_collection.natural_harmonic_node_list.append(node)
        note.playing_indicator_collection.natural_harmonic_node_list.parenthesize_lower_note_head = (
            True
        )

        if natural_harmonic.index > 5:
            contact_point = "arco"

    note.playing_indicator_collection.string_contact_point.contact_point = contact_point
    if contact_point != "pizzicato":
        note.notation_indicator_collection.duration_list.is_active = True

    simultaneous_event[0].append(note)


def pop_harp(
    pitch_set,
    pitch_count_dict,
    duration,
    simultaneous_event,
    instrument,
    random,
    chord_index,
    max_chord_index,
):
    while len(simultaneous_event) < 2:
        simultaneous_event.append(core_events.SequentialEvent())

    pitch = generic_pitch_popper(pitch_set, pitch_count_dict, instrument, random)
    if pitch is None:
        return add_rest(simultaneous_event, duration)

    t_right, t_left = project_utilities.split_harp(
        core_events.SequentialEvent(
            [music_events.NoteLike(pitch, duration=duration, volume="ppp")]
        )
    )

    right, left = simultaneous_event

    right.extend(t_right)
    left.extend(t_left)

    if max_chord_index == chord_index:  # is_last
        if not left[-1].pitch_list:
            left[-1].pitch_list = (
                music_parameters.JustIntonationPitch("1/6"),
                music_parameters.JustIntonationPitch("1/3"),
            )
            left[-1].playing_indicator_collection.cluster.is_active = True


def pop_generic(
    pitch_set,
    pitch_count_dict,
    duration,
    simultaneous_event,
    instrument,
    random,
    chord_index,
    max_chord_index,
):
    if not simultaneous_event:
        simultaneous_event.append(core_events.SequentialEvent())

    pitch = generic_pitch_popper(pitch_set, pitch_count_dict, instrument, random)
    if pitch is None:
        return add_rest(simultaneous_event, duration)

    simultaneous_event[0].append(
        music_events.NoteLike(pitch, duration=duration, volume="ppp")
    )


def generic_pitch_popper(pitch_set, pitch_count_dict, instrument, random):
    if not pitch_count_dict:
        return

    min_pitch_count = min(pitch_count_dict.values())

    pitch_list = []
    for pitch in pitch_set:
        if (
            pitch_count_dict[pitch.normalize(mutate=False).exponent_tuple]
            == min_pitch_count
        ):
            pitch_list.extend(instrument.get_pitch_variant_tuple(pitch))

    if not pitch_list:
        return

    pitch = random.choice(pitch_list)
    pitch_count_dict[pitch.normalize(mutate=False).exponent_tuple] += 1

    return pitch


def add_rest(simultaneous_event, duration):
    for seq in simultaneous_event:
        seq.append(music_events.NoteLike(duration=duration))


TOLERANCE = music_parameters.DirectPitchInterval(5)
