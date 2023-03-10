import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import timeline_interfaces


def is_supported(context, scale_harp, **kwargs):
    return scale_harp.is_supported(context, **kwargs)


def main(
    context, random, activity_level, scale_harp, **kwargs
) -> timeline_interfaces.EventPlacement:
    pitch_tuple_tuple = scale_harp(context, **kwargs)
    modal_event_to_convert = context.modal_event
    instrument = context.orchestration[0]
    tag = instrument.name

    last_duration = 4

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
    if len(melody[-2].pitch_list) > 1:
        melody[-1].duration = last_duration / 2
        melody[-2].duration = last_duration / 2
    else:
        melody[-1].duration = last_duration

    add_optional(melody)
    add_arpeggio(melody, activity_level)
    add_pitch_variation(melody, activity_level)
    # Deactivated, not so good
    # add_repetition(melody, activity_level)

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


def add_optional(melody):
    """If we have a small interval, a note inbetween can be optional"""
    for index, note_like in enumerate(melody[1:-1]):
        scale_pitch, scale_pitch_before, scale_pitch_after = (
            max(n.pitch_list) for n in (note_like, melody[index - 1], melody[index + 1])
        )
        interval0, interval1 = (
            abs((scale_pitch - other).interval)
            for other in (scale_pitch_before, scale_pitch_after)
        )
        summed_interval = interval0 + interval1
        if summed_interval < 350:
            note_like.playing_indicator_collection.optional = True
            break  # only one optional note per event placement


def add_arpeggio(melody, activity_level):
    if len(melody[0].pitch_list) > 1 and activity_level(6):
        melody[0].playing_indicator_collection.arpeggio.direction = "up"


def add_pitch_variation(melody, activity_level):
    if (
        len(melody) == 4
        # We don't want a pitch variation if the second note is optional,
        # because this could result in a pitch repetition when the optional
        # note is omitted.
        and (not melody[1].playing_indicator_collection.optional.is_active)
        and activity_level(4)
    ):
        melody[2].pitch_list = max(melody[0].pitch_list)


def add_repetition(melody, activity_level):
    if activity_level(3):
        melody.split_child_at(
            melody.absolute_time_tuple[-1] + (melody[-1].duration * 0.5)
        )
