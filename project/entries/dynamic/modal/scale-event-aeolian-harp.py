import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import timeline_interfaces


def is_supported(context, scale, **kwargs):
    return scale.is_supported(context, **kwargs)


def main(
    context, random, activity_level, scale, **kwargs
) -> timeline_interfaces.EventPlacement:
    pitch_tuple_tuple = scale(context, **kwargs)
    modal_event_to_convert = context.modal_event
    instrument = context.orchestration[0]
    tag = instrument.name

    melody = core_events.SequentialEvent(
        [
            music_events.NoteLike(
                pitch_tuple,
                random.choice([1.0, 1.5, 2.0, 2.5]),
                "pp",
            )
            for pitch_tuple in pitch_tuple_tuple
        ]
    )
    duration = modal_event_to_convert.clock_event.duration
    start_range = ranges.Range(duration * 0, duration * 0.3)
    end_range = ranges.Range(duration * 0.7, duration * 0.98)

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent(
            [core_events.TaggedSimultaneousEvent([melody], tag=tag)]
        ),
        start_range,
        end_range,
    ).move_by(context.start)
