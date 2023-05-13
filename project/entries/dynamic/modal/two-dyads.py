import fractions
import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import project_utilities
from mutwo import timeline_interfaces


def get_pitch_tuple(context):
    modal_event = context.modal_event
    return (modal_event.start_pitch, modal_event.end_pitch)


def is_supported(context, dyad, **kwargs):
    try:
        pitch_tuple = get_pitch_tuple(context)
    except AttributeError:
        return False

    if context.index % 3 == 0:
        return False

    return dyad.is_supported(
        context, pitch=pitch_tuple[0], **kwargs
    ) and dyad.is_supported(context, pitch=pitch_tuple[1], **kwargs)


def main(context, dyad, random, **kwargs) -> timeline_interfaces.EventPlacement:
    pitch0, pitch1 = get_pitch_tuple(context)
    dyad0 = dyad(context, pitch=pitch0, prohibited_pitch_list=[pitch1], **kwargs)
    dyad1 = dyad(context, pitch=pitch1, prohibited_pitch_list=dyad0, **kwargs)
    dyad_tuple = (dyad0, dyad1)
    modal_event_to_convert = context.modal_event
    instrument = context.orchestration[0]
    tag = instrument.name
    duration = modal_event_to_convert.clock_event.duration

    real_duration = fractions.Fraction(20, 16)
    if real_duration > duration:
        real_duration = duration

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

    melody = core_events.SequentialEvent(
        [
            music_events.NoteLike(
                dyad,
                random.choice([0.5, 1, 0.75, 0.25]),
                "p",
            )
            for dyad in dyad_tuple
        ]
    )

    simultaneous_event = core_events.SimultaneousEvent(
        [core_events.TaggedSimultaneousEvent([melody], tag=tag)]
    )

    return timeline_interfaces.EventPlacement(
        simultaneous_event,
        start_range,
        end_range,
    ).move_by(context.start)
