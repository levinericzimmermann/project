from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters


__all__ = ("split_harp",)


def split_harp(
    harp_event: core_events.SequentialEvent, tag="harp"
) -> core_events.SimultaneousEvent:
    border = music_parameters.WesternPitch("c", 4)
    right = harp_event.set_parameter(
        "pitch_list",
        lambda pitch_list: [p for p in pitch_list if p >= border]
        if pitch_list
        else None,
        mutate=False,
    )
    left = harp_event.set_parameter(
        "pitch_list",
        lambda pitch_list: [p for p in pitch_list if p < border]
        if pitch_list
        else None,
        mutate=False,
    )

    for note_like in left:
        if notation_indicator_collection := getattr(
            note_like, "notation_indicator_collection", None
        ):
            notation_indicator_collection.clef.name = "bass"
            break

    for seq in (right, left):
        for e in seq:
            if not e.pitch_list:
                e.playing_indicator_collection = (
                    music_events.configurations.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS()
                )

    return core_events.TaggedSimultaneousEvent([left, right], tag=tag)
