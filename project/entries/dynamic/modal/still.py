"""Present, moving, but about one pitch.

1. We have the present pitch + its neighbours,
2. Player can pick octave & whether a tone is played/repeated.
3. All three pitches (present + neighbours) do have alterations.
4. Depending on the stability of the current context we have more/less
   alterations.
5. We also must decide which neighbour we prefer (how much).
6. Sometimes we may want to add chords between main pitch + harmonic
   neighbour.

This entry needs the additional kwargs 'instrument_scale' and 'global_scale'
and 'instrument_scale_with_alterations'.

'instrument_scale' and 'global_scale' should return more or less the same pitch
if we call '.scale_position_to_pitch' on them. We differentiate between
'global_scale' and 'instrument_scale' to support the case of an instrument
which uses slightly different intonations than what the global scales asks for
(for instance due to limitations of the instruments).

'instrument_scale_with_alterations' has the same pitches like
'instrument_scale', but with some additional pitches which are not part
of the normal scale, but which can nevertheless be played on the instrument
('harmoniefremde Tonhoehen').
"""

import collections

import quicktions as fractions

import ranges
import yamm

from mutwo import core_events
from mutwo import clock_events
from mutwo import music_events
from mutwo import music_parameters


def is_supported(context, **kwargs):
    try:
        assert isinstance(context.modal_event, clock_events.ModalEvent1)
        orchestration = context.orchestration
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert isinstance(instrument, music_parameters.DiscreetPitchedInstrument)
    except AssertionError:
        return False
    return True


DEFAULT_SCALE = music_parameters.Scale(
    music_parameters.JustIntonationPitch("1/1"),
    music_parameters.ScaleFamily((music_parameters.JustIntonationPitch("1/1"),)),
)


def main(
    context,
    random,
    activity_level,
    global_scale=DEFAULT_SCALE,
    instrument_scale=None,
    instrument_scale_with_alterations=None,
    **kwargs,
) -> core_events.SimultaneousEvent:
    orchestration = context.orchestration
    instrument = orchestration[0]
    modal_event = context.modal_event
    scale = modal_event.scale
    main_pitch = modal_event.pitch
    duration = modal_event.clock_event.duration

    if instrument_scale is None:
        instrument_scale = global_scale
    if instrument_scale_with_alterations is None:
        instrument_scale_with_alterations = instrument_scale

    assert global_scale.scale_degree_count == instrument_scale.scale_degree_count

    sequential_event = make_sequential_event(
        main_pitch,
        duration,
        instrument,
        scale,
        random,
        global_scale,
        instrument_scale,
        instrument_scale_with_alterations,
        activity_level,
    )

    simultaneous_event = core_events.SimultaneousEvent(
        [
            core_events.TaggedSimultaneousEvent(
                [sequential_event],
                tag=instrument.name,
            )
        ]
    )

    return simultaneous_event


def make_sequential_event(
    main_pitch,
    duration,
    instrument,
    scale,
    random,
    global_scale,
    instrument_scale,
    instrument_scale_with_alterations,
    activity_level,
):
    pitch_material = get_pitch_material(
        main_pitch,
        scale,
        instrument,
        global_scale,
        instrument_scale,
        instrument_scale_with_alterations,
    )

    sequential_event = core_events.SequentialEvent([])

    event_count = duration_to_event_count(duration)
    g = markov_chain.walk((0,))
    event_counter = 0
    while event_counter < event_count:
        pindex = next(g)
        pitch_part = pitch_material[pindex]

        # Main pitch has more repetitions
        if pindex == 0:
            rcount_option_tuple = (1, 2, 3)
        # Side pitches have fewer repetitions
        else:
            rcount_option_tuple = (1, 2)
        repetition_count = random.choice(rcount_option_tuple)

        repetition_count = min((event_count - event_counter, repetition_count))

        for _ in range(repetition_count):

            if main_part := activity_level(7):
                pitch = pitch_part.pitch
            else:
                if activity_level(5):
                    pitch = pitch_part.alteration_up
                else:
                    pitch = pitch_part.alteration_down

            n = music_events.NoteLike(pitch, 1, "pp")

            # Alteration
            if not main_part:
                x = 0.5
            # Main note, not alteration
            elif pindex == 0:
                x = 1.5
            # Side note, not alteration
            else:
                x = 1

            note_head = rf"\filled-box #'(0 . {x}) #'(-0.5 . 0.5) #0"
            n.notation_indicator_collection.note_head.markup_content = note_head

            sequential_event.append(n)
            event_counter += 1

    return sequential_event


def get_pitch_material(
    main_pitch,
    scale,
    instrument,
    global_scale,
    instrument_scale,
    instrument_scale_with_alterations,
):
    main_pitch, scale_position = pitch_to_normalized_instrument_pitch(
        main_pitch, global_scale, instrument_scale
    )

    neighbour_pitch_list = []
    for d in (-1, 1):
        p = ((scale_position[0] + d) % global_scale.scale_degree_count, 0)
        n = instrument_scale.scale_index_to_pitch(p[0])
        assert n != main_pitch
        neighbour_pitch_list.append(n)

    pitch_part = collections.namedtuple(
        "pitch_part", ("pitch", "alteration_down", "alteration_up")
    )

    pitch_material = []
    scale_degree_count = instrument_scale_with_alterations.scale_degree_count
    for p in [main_pitch] + neighbour_pitch_list:
        alteration_list = []
        pos = instrument_scale_with_alterations.pitch_to_scale_position(p)
        for d in (-1, 1):
            local_pos = ((pos[0] + d) % scale_degree_count, 0)
            alteration_list.append(
                instrument_scale_with_alterations.scale_index_to_pitch(local_pos[0])
            )
        part = pitch_part(p, *alteration_list)
        pitch_material.append(part)

    return collections.namedtuple(
        "pitch_material", ("main_pitch", "neighbour_down", "neighbour_up")
    )(*pitch_material)


def pitch_to_normalized_instrument_pitch(pitch, global_scale, instrument_scale):
    scale_position = global_scale.pitch_to_scale_position(pitch)
    normalized_scale_position = (scale_position[0], 0)
    normalized_instrument_pitch = instrument_scale.scale_index_to_pitch(
        normalized_scale_position[0]
    )
    return (
        normalized_instrument_pitch,
        normalized_scale_position,
    )


def duration_to_event_count(duration):
    return int(duration / density[0]) * density[1]


markov_chain = yamm.chain.Chain(
    {
        (0,): {1: 1, 2: 1},
        (1,): {0: 1, 2: 0.25},
        (2,): {0: 1, 1: 0.25},
    }
)


# For 10 seconds 1 attack
density = (fractions.Fraction(10, 16), 1)
