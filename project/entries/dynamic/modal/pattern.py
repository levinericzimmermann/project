import fractions

import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_events
from mutwo import project_generators
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, pitch=None, **kwargs):
    try:
        assert context.modal_event.pitch is not None
        assert isinstance(context.modal_event, clock_events.ModalEvent1)
        orchestration = context.orchestration
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert isinstance(instrument, music_parameters.abc.PitchedInstrument)
        assert instrument.name in ("glockenspiel",)
        pitch = pitch or get_pitch(context)
        assert instrument.get_pitch_variant_tuple(pitch)
        assert context.index != 0
        assert (context.index % 4) != 3
    except AssertionError:
        return False
    return True


def main(
    context, random, activity_level, pitch=None, **kwargs
) -> timeline_interfaces.EventPlacement:
    orchestration = context.orchestration
    instrument = orchestration[0]
    scale = context.modal_event.scale
    pitch = pitch or get_pitch(context)
    main_pitch_tuple = instrument.get_pitch_variant_tuple(pitch)

    match context.index % 4:
        case 0:
            real_duration = fractions.Fraction(20, 16)
            bal = 0.7
        case 1:
            real_duration = fractions.Fraction(20, 16)
            bal = 0.7
        case 2:
            real_duration = fractions.Fraction(20, 16)
            bal = 0.7
        case 3:
            real_duration = fractions.Fraction(15, 16)
            bal = 0.5

    duration = context.modal_event.clock_event.duration
    if real_duration > duration:
        real_duration = duration
    start_range, end_range = project_utilities.get_ranges(real_duration, duration, bal)

    event_count = duration_to_event_count(real_duration)

    chord_tuple = project_generators.find_chord_tuple(
        (main_pitch_tuple[0],),
        # No pitches..
        # tuple(p for p in instrument.pitch_tuple if p in scale.pitch_tuple),
        instrument.pitch_tuple,
        ranges.Range(3, 4),
        # Disallow octaves by only allowing intervals smaller than
        # big seventh
        max_interval=music_parameters.JustIntonationPitch("15/8"),
    )
    champion, fitness = None, None
    for c in chord_tuple:
        if not champion or c.harmonicity > fitness:
            champion, fitness = c, c.harmonicity
    if champion is not None:
        chord = champion.pitch_tuple
    else:
        chord = (main_pitch_tuple[0],)

    available_pitch_list = []
    for p in chord:
        available_pitch_list.extend(instrument.get_pitch_variant_tuple(p))

    available_pitch_list = sorted(available_pitch_list)
    max_index = len(available_pitch_list) - 1

    last_pitch = available_pitch_list[available_pitch_list.index(main_pitch_tuple[0])]

    sequential_event = core_events.SequentialEvent([])
    for _ in range(event_count):
        previous_index = available_pitch_list.index(last_pitch)
        if previous_index == 0:
            index = 1
        elif previous_index == max_index:
            index = max_index - 1
        else:
            index = previous_index + (-1, 1)[activity_level(5)]

        if index > max_index:
            index = max_index

        pitch = last_pitch = available_pitch_list[index]

        pitch_list = [pitch]
        if index == 0:
            pitch_list.append(available_pitch_list[-1])
        elif index == max_index:
            pitch_list.append(available_pitch_list[0])
        else:
            if (pitch in main_pitch_tuple and activity_level(6)) or activity_level(3):
                pitch_list = instrument.get_pitch_variant_tuple(pitch)

        duration_tuple = (
            (2, 1.75, 2.5) if pitch in main_pitch_tuple else (1, 1.25, 0.75)
        )
        note = music_events.NoteLike(pitch_list, random.choice(duration_tuple), "pp")
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


def get_pitch(context):
    return context.modal_event.pitch


def duration_to_event_count(duration):
    return int(duration / density[0]) * density[1]


# For 10 seconds 1 attack
density = (fractions.Fraction(5, 16), 1)
