import quicktions as fractions
import ranges

from mutwo import clock_events
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters
from mutwo import project_utilities
from mutwo import timeline_interfaces


def is_supported(context, scale_harp, **kwargs):
    return scale_harp.is_supported(context, **kwargs)


def main(
    context, random, activity_level, scale_harp, **kwargs
) -> timeline_interfaces.EventPlacement:
    scale = context.modal_event.scale
    end_pitch = context.modal_event.end_pitch
    pitch_tuple_tuple = scale_harp(context, **kwargs)
    modal_event_to_convert = context.modal_event
    instrument = context.orchestration[0]
    tag = instrument.name
    duration = modal_event_to_convert.clock_event.duration

    real_duration = fractions.Fraction(25, 16)
    if real_duration > duration:
        real_duration = duration
    start_range, end_range = project_utilities.get_ranges(real_duration, duration, 0.5)

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
    if has_inversion := (len(melody[-2].pitch_list) > 1):
        melody[-1].duration = last_duration / 2
        melody[-2].duration = last_duration / 2
    else:
        melody[-1].duration = last_duration

    add_optional(melody)
    add_arpeggio(melody, activity_level, has_inversion)
    add_pitch_variation(melody, activity_level)
    add_staccatto(melody, activity_level, random, has_inversion)
    xylophone = add_xylophone(melody, activity_level)
    if not xylophone:
        add_cluster(melody, scale, activity_level, random, has_inversion)
        add_flageolet(melody, activity_level, random, has_inversion)

    harp_event = project_utilities.split_harp(melody, tag)
    for hand in harp_event:
        add_accent(hand, scale, end_pitch, has_inversion, activity_level)

    return timeline_interfaces.EventPlacement(
        core_events.SimultaneousEvent([harp_event]), start_range, end_range
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


def add_arpeggio(melody, activity_level, has_inversion):
    if has_inversion and len(melody[-1].pitch_list) > 1:
        if activity_level(6):
            melody[-1].playing_indicator_collection.arpeggio.direction = "down"
        return
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


def add_cluster(melody, scale, activity_level, random, has_inversion):
    if has_inversion:
        index = -2
    else:
        index = -1

    if activity_level(3):
        start_pitch = random.choice(
            [scale.scale_position_to_pitch((i, 0)) for i in range(5)]
        )
        p0, p1 = (
            start_pitch - music_parameters.JustIntonationPitch(r)
            for r in "16/1 8/1".split(" ")
        )
        n = music_events.NoteLike((p0, p1), fractions.Fraction(1, 4), volume="ppp")
        n.playing_indicator_collection.cluster.is_active = True
        melody.insert(index, n)


def add_xylophone(melody, activity_level) -> bool:
    if all(
        [len(p) <= 1 for p in melody.get_parameter("pitch_list")]
    ) and activity_level(7):
        for n in melody[:-1]:
            n.playing_indicator_collection.sons_xylo.activity = True
        melody[-1].playing_indicator_collection.sons_xylo.activity = False
        return True
    return False


def add_staccatto(melody, activity_level, random, has_inversion):
    if (note_count := len(melody)) > 3 and activity_level(5):
        note_to_pick_index_range_max = note_count - 2 - int(has_inversion)
        staccatto_count = random.choice((1, 2), p=(0.6, 0.4))
        note_to_pick_index_list = random.choice(
            tuple(range(1, note_to_pick_index_range_max + 1)), size=staccatto_count
        )
        for note_to_pick_index in note_to_pick_index_list:
            if (
                n := melody[note_to_pick_index]
            ).playing_indicator_collection.cluster.is_active:
                continue
            n.playing_indicator_collection.articulation.name = "."


def add_flageolet(melody, activity_level, random, has_inversion):
    if (note_count := len(melody)) > 3 and activity_level(8):
        note_to_pick_index_range_max = note_count - 2 - int(has_inversion)
        f_count = random.choice((1, 2, 3), p=(0.5, 0.3, 0.2))
        min_index = 0 if len(melody[0].pitch_list) == 1 else 1
        note_to_pick_index_list = random.choice(
            tuple(range(min_index, note_to_pick_index_range_max + 1)), size=f_count
        )
        for note_to_pick_index in note_to_pick_index_list:
            n = melody[note_to_pick_index]
            if len(n.pitch_list) != 1:
                continue
            p = n.playing_indicator_collection
            if p.cluster.is_active or p.articulation.is_active or p.optional.is_active:
                continue
            n.playing_indicator_collection.flageolet.is_active = True
            n.pitch_list[0] -= music_parameters.JustIntonationPitch("2/1")


def add_accent(melody, scale, end_pitch, has_inversion, activity_level):
    normalized_end_pitch = end_pitch.normalize(mutate=False)
    stop_index = -1 if has_inversion else None
    for i, e in enumerate(reversed(melody[:stop_index])):
        # No accents for flageolets, those are rather quite sounds
        if e.playing_indicator_collection.flageolet.is_active:
            continue

        add_accent = False
        for p in e.pitch_list:
            if p.normalize(mutate=False) == normalized_end_pitch:
                add_accent = True
        if add_accent and ((i == 0 and activity_level(6)) or activity_level(2)):
            e.playing_indicator_collection.articulation.name = ">"
            e.volume = "mf"
