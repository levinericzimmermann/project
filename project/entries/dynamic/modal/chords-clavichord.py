import itertools
import operator
import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_events
from mutwo import project_parameters
from mutwo import timeline_interfaces


def is_supported(context, pitch=None, **kwargs):
    try:
        assert isinstance(context.modal_event, clock_events.ModalEvent1)
        orchestration = context.orchestration
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert isinstance(instrument, project_parameters.Clavichord)
    except AssertionError:
        return False
    return True


def main(
    context, random, activity_level, **kwargs
) -> timeline_interfaces.EventPlacement:
    orchestration = context.orchestration
    instrument = orchestration[0]
    scale = context.modal_event.scale

    simultaneous_event = core_events.SimultaneousEvent(
        [
            core_events.TaggedSimultaneousEvent(
                [
                    core_events.SequentialEvent(
                        [
                            music_events.NoteLike(
                                [
                                    random.choice(instrument.pitch_tuple),
                                    random.choice(instrument.pitch_tuple),
                                    random.choice(instrument.pitch_tuple),
                                ],
                                volume="p",
                                duration=random.choice([1, 1.5, 0.75]),
                            )
                            for _ in range(random.choice([2, 3, 4]))
                        ]
                    )
                ],
                tag=instrument.name,
            )
        ]
    )

    duration = context.modal_event.clock_event.duration
    start_range = ranges.Range(duration * 0.3, duration * 0.35)
    end_range = ranges.Range(duration * 0.65, duration * 0.7)
    # start_range = ranges.Range(duration * 0.04, duration * 0.045)
    # end_range = ranges.Range(duration * 0.955, duration * 0.9999999999999999996)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)
