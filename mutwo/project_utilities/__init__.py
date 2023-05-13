import ranges

from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters


__all__ = ("split_harp", "get_ranges")


def split_harp(
    harp_event: core_events.SequentialEvent,
    tag="harp",
    split_border: music_parameters.abc.Pitch = music_parameters.WesternPitch("cqf", 4),
) -> core_events.SimultaneousEvent:
    right = core_events.TaggedSequentialEvent(
        harp_event.set_parameter(
            "pitch_list",
            lambda pitch_list: [p for p in pitch_list if p >= split_border]
            if pitch_list
            else None,
            mutate=False,
        ),
        tag="right",
    )
    left = core_events.TaggedSequentialEvent(
        harp_event.set_parameter(
            "pitch_list",
            lambda pitch_list: [p for p in pitch_list if p < split_border]
            if pitch_list
            else None,
            mutate=False,
        ),
        tag="left",
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

    return core_events.TaggedSimultaneousEvent([right, left], tag=tag)


# balance:
#   0.0: all delay at the end
#   0.5: equal at the beginning and at the end
#   1.0: all delay at the beginning
def get_ranges(needed_duration, duration, balance):
    assert balance >= 0 and balance <= 1

    remaining = duration - needed_duration
    assert remaining >= 0

    left, right = remaining * balance, remaining * (1 - balance)
    right = duration - right
    # return ranges.Range(left, left * 0.01), ranges.Range(right * 0.99, right)
    return left, right
