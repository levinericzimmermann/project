import quicktions as fractions

from mutwo import core_events
from mutwo import common_generators
from mutwo import diary_interfaces
from mutwo import music_events
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, **kwargs):
    try:
        assert isinstance(context, diary_interfaces.ModalContext0)
        assert context.modal_event.start_pitch != context.modal_event.end_pitch
        orchestration = context.orchestration
        assert len(orchestration) == 1
        instrument = orchestration[0]
        assert instrument.name in ("glockenspiel",)
        assert context.energy > 50
    except AssertionError:
        return False
    return True


def main(
    context, random, activity_level, scale, **kwargs
) -> timeline_interfaces.EventPlacement:
    modal_event_to_convert = context.modal_event
    instrument = context.orchestration[0]
    duration = modal_event_to_convert.clock_event.duration

    real_duration = fractions.Fraction(22, 16)
    if real_duration > duration:
        real_duration = duration

    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

    pitch_tuple_list = []
    for direction in (True, False):
        pitch_tuple = scale(context, direction=direction, octave_count=0, **kwargs)
        pitch_tuple_list.append((len(pitch_tuple), pitch_tuple))

    pitch_tuple = max(pitch_tuple_list, key=lambda p: p[0])[1]

    pitch_count = len(pitch_tuple)
    if pitch_count > 4:
        allowed_pitch_tuple = common_generators.euclidean(pitch_count - 1, 3)
        pitch_list = []
        for p, is_allowed in zip(pitch_tuple, allowed_pitch_tuple):
            if is_allowed:
                pitch_list.append(p)
        pitch_list.append(pitch_tuple[-1])

        pitch_tuple = tuple(pitch_list)

    if context.energy >= 60:
        bow_level = 10
    elif context.energy >= 55:
        bow_level = 8
    elif context.energy >= 50:
        bow_level = 6

    use_bow = activity_level(bow_level)

    sequential_event = core_events.SequentialEvent([])
    is_first = True
    for p in pitch_tuple:
        n = music_events.NoteLike(p, 1.5, "ppp")
        if use_bow:
            n.notation_indicator_collection.duration_line.is_active = True
            if not is_first:
                sequential_event.append(
                    music_events.NoteLike(duration=random.choice([0.25, 0.5, 0.75]))
                )
        sequential_event.append(n)
        is_first = False

    simultaneous_event = core_events.TaggedSimultaneousEvent(
        [sequential_event], tag=instrument.name
    )

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([simultaneous_event]), start_range, end_range
    ).move_by(context.start)


def duration_to_event_count(duration):
    return int(duration / density[0]) * density[1]


density = (fractions.Fraction(9, 16), 1)
