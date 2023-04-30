import ranges

from mutwo import timeline_interfaces

import project


def is_supported(context, still, **kwargs):
    return still.is_supported(context, **kwargs)


def main(context, still, **kwargs) -> timeline_interfaces.EventPlacement:
    simultaneous_event = still(
        context,
        global_scale=project.constants.SCALE,
        instrument_scale=project.constants.GLOCKENSPIEL_SCALE,
        instrument_scale_with_alterations=project.constants.GLOCKENSPIEL_SCALE,
        **kwargs
    )

    duration = context.modal_event.clock_event.duration

    if context.index == 0:
        start_range = ranges.Range(duration * 0.4, duration * 0.5)
    else:
        start_range = ranges.Range(duration * 0.01, duration * 0.1)
    end_range = ranges.Range(duration * 0.95, duration * 0.995)

    return timeline_interfaces.EventPlacement(
        simultaneous_event, start_range, end_range
    ).move_by(context.start)
