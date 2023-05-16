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
    except AssertionError:
        return False
    return alternating_scale_chords.is_supported(context, **kwargs)


def main(context, alternating_scale_chords, random, **kwargs):
    chord_tuple = alternating_scale_chords(context, **kwargs)

    modal_event_to_convert = context.modal_event
    duration = modal_event_to_convert.clock_event.duration

    real_duration = fractions.Fraction(37, 16)
    if real_duration > duration:
        real_duration = duration

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.35)

    simultaneous_event = core_events.SimultaneousEvent(
        [
            core_events.TaggedSimultaneousEvent(
                [core_events.SequentialEvent([])], tag=instrument.name
            )
            for instrument in context.orchestration
        ]
    )

    for chord in chord_tuple:
        duration = random.choice([1, 1.5, 0.75])
        distribute_chord(
            duration, chord, simultaneous_event, context.orchestration, random
        )

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


def distribute_chord(duration, chord, simultaneous_event, orchestration, random):
    instrument_pitch_data_list = []
    for instrument in orchestration:
        playable_pitch_count = 0
        pitch_variant_list = []
        for p in chord:
            if t := instrument.get_pitch_variant_tuple(p):
                playable_pitch_count += 1
            pitch_variant_list.append(t)
        instrument_pitch_data_list.append(
            (instrument, playable_pitch_count, pitch_variant_list)
        )

    pitch_count_dict = {p.exponent_tuple: 0 for p in chord}
    for instrument, _, pitch_variant_list in sorted(
        instrument_pitch_data_list, key=lambda d: d[1]
    ):
        pitch_variant_options_list = []
        for p, pitch_variant_tuple in zip(chord, pitch_variant_list):
            if pitch_variant_tuple:
                pitch_variant_options_list.append(
                    (pitch_count_dict[p.exponent_tuple], p, pitch_variant_tuple)
                )
        if pitch_variant_options_list:
            _, p, pitch_variant_tuple = sorted(
                pitch_variant_options_list, key=lambda d: d[0]
            )[0]
            pitch_count_dict[p.exponent_tuple] += 1
            n = music_events.NoteLike(random.choice(pitch_variant_tuple), duration, "pp")
            if instrument.name in ("v",):
                n.playing_indicator_collection.string_contact_point.contact_point = (
                    "pizzicato"
                )
        else:
            n = music_events.NoteLike([], duration, "p")
        simultaneous_event[instrument.name][0].append(n)
