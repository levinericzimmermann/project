import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_events
from mutwo import timeline_interfaces


def is_supported(context, scale, **kwargs):
    return scale.is_supported(context, **kwargs)


def main(
    context, random, activity_level, scale, **kwargs
) -> timeline_interfaces.EventPlacement:
    pitch_tuple = scale(context, **kwargs)
    modal_event_to_convert = context.modal_event
    instrument = context.orchestration[0]
    tag = instrument.name

    sim = core_events.TaggedSimultaneousEvent(
        [core_events.SequentialEvent([]) for _ in range(instrument.TOTAL_STRING_COUNT)],
        tag=tag,
    )

    absolute_time = core_parameters.DirectDuration(0)
    for pitch in pitch_tuple:
        duration = random.choice([1.0, 1.5, 2.0, 2.5])
        for sindex, string in enumerate(instrument.string_tuple):
            if string.tuning == pitch:
                seq = sim[sindex]
                if diff := (absolute_time - seq.duration):
                    seq.append(core_events.SimpleEvent(diff))
                seq.append(music_events.NoteLike(pitch, duration=duration, volume="p"))
        absolute_time += duration

    sim.extend_until()

    duration = modal_event_to_convert.clock_event.duration
    start_range = ranges.Range(duration * 0, duration * 0.3)
    end_range = ranges.Range(duration * 0.7, duration * 0.98)

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([sim]),
        start_range,
        end_range,
    ).move_by(context.start)
