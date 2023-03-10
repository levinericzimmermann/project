import copy
import typing

import quicktions as fractions

from mutwo import core_constants
from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_converters
from mutwo import music_parameters


__all__ = ("TremoloConverter",)


class TremoloConverter(music_converters.PlayingIndicatorConverter):
    """Apply tremolo on :class:`~mutwo.core_events.SimpleEvent`.

    :param simple_event_to_playing_indicator_collection: Function to extract from a
        :class:`mutwo.core_events.SimpleEvent` a
        :class:`mutwo.ext.parameters.playing_indicators.PlayingIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.ext.events.music.NoteLike.playing_indicator_collection`
        attribute (because by default :class:`mutwo.ext.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.ext.events.music.NoteLike`
        with a different name for their playing_indicator_collection property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no playing indicator
        collection can be extracted), mutwo will build a playing indicator collection
        from :const:`~mutwo.music_events.configurations.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS`.
    :type simple_event_to_playing_indicator_collection: typing.Callable[[core_events.SimpleEvent], music_parameters.PlayingIndicatorCollection,], optional
    """

    def __init__(
        self,
        min_duration: core_parameters.abc.Duration
        | float = core_parameters.DirectDuration(0.25),
        max_duration: core_parameters.abc.Duration
        | float = core_parameters.DirectDuration(0.95),
        simple_event_to_playing_indicator_collection: typing.Callable[
            [core_events.SimpleEvent],
            music_parameters.PlayingIndicatorCollection,
        ] = music_converters.SimpleEventToPlayingIndicatorCollection(),
    ):
        min_duration = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(
            min_duration
        )
        max_duration = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(
            max_duration
        )
        self._average_duration = average_duration = (
            (max_duration - min_duration) * fractions.Fraction(1, 2)
        ) + min_duration
        self._d_none = [[0, average_duration], [1, average_duration]]
        self._d_acc = [[0, max_duration], [1, min_duration]]
        self._d_rit = [[0, min_duration], [1, max_duration]]
        self._d_rit_acc = [[0, min_duration], [0.5, max_duration], [1, min_duration]]
        self._d_acc_rit = [
            # [0, max_duration, -1],
            [0, max_duration, -6],
            # [0.5, min_duration, 2],
            [0.5, min_duration, 4],
            [1, max_duration],
        ]
        super().__init__(simple_event_to_playing_indicator_collection)

    def _apply_playing_indicator(
        self,
        simple_event_to_convert: core_events.SimpleEvent,
        playing_indicator: music_parameters.Tremolo,
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        D = music_parameters.Tremolo.D
        s_dur = simple_event_to_convert.duration
        event_count = int(s_dur / self._average_duration)
        match playing_indicator.dynamic:
            case D.Acc:
                point_list = self._d_acc
            case D.Rit:
                point_list = self._d_rit
            case D.AccRit:
                point_list = self._d_acc_rit
            case D.RitAcc:
                point_list = self._d_rit_acc
            case _:
                point_list = self._d_none
        duration_envelope = core_events.Envelope(point_list)
        sequential_event = core_events.SequentialEvent([])
        max_event_index = event_count - 1
        for event_index in range(event_count):
            sequential_event.append(
                simple_event_to_convert.set(
                    "duration",
                    duration_envelope.value_at(event_index / max_event_index),
                    mutate=False,
                )
            )
        return sequential_event.set("duration", s_dur)

    @property
    def playing_indicator_name(self) -> str:
        return "tremolo"

    @property
    def default_playing_indicator(self) -> music_parameters.abc.PlayingIndicator:
        return music_parameters.Tremolo()
