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
    except AssertionError:
        return False
    return alternating_scale_chords.is_supported(context, **kwargs)


def main(context, alternating_scale_chords, **kwargs):
    chord_tuple = alternating_scale_chords(context, **kwargs)

    modal_event_to_convert = context.modal_event
    duration = modal_event_to_convert.clock_event.duration

    real_duration = fractions.Fraction(37, 16)
    if real_duration > duration:
        real_duration = duration

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

    simultaneous_event = core_events.SimultaneousEvent(
        [
            core_events.TaggedSimultaneousEvent(
                [core_events.SequentialEvent([])], tag=instrument.name
            )
            for instrument in context.orchestration
        ]
    )

    for chord in chord_tuple:
        distribute_chord(chord, simultaneous_event, context.orchestration)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)


def distribute_chord(chord, simultaneous_event, orchestration):
    for instrument in orchestration:
        added = False
        for p in chord:
            t = instrument.get_pitch_variant_tuple(p)
            if added := t:
                n = music_events.NoteLike(t[len(t) // 2], 1, "p")
                simultaneous_event[instrument.name][0].append(n)
                break
        if not added:
            n = music_events.NoteLike([], 1, "p")
            simultaneous_event[instrument.name][0].append(n)
