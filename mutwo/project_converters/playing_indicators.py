import typing
import warnings

import quicktions as fractions

from mutwo import core_constants
from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_converters
from mutwo import music_events
from mutwo import music_parameters

__all__ = (
    "TremoloConverter",
    "ClusterConverter",
    "FlageoletConverter",
    "BendAfterConverter",
    "BridgeConverter",
    "MovingOverpressureConverter",
    "BowedBoxConverter",
)


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


class ClusterConverter(music_converters.PlayingIndicatorConverter):
    def __init__(
        self,
        scale: music_parameters.Scale,
        simple_event_to_playing_indicator_collection: typing.Callable[
            [core_events.SimpleEvent],
            music_parameters.PlayingIndicatorCollection,
        ] = music_converters.SimpleEventToPlayingIndicatorCollection(),
    ):
        self.scale = scale
        super().__init__(simple_event_to_playing_indicator_collection)

    def _apply_playing_indicator(
        self,
        simple_event_to_convert: core_events.SimpleEvent,
        playing_indicator: music_parameters.abc.ExplicitPlayingIndicator,
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        sequential_event = core_events.SequentialEvent([])
        simple_event_to_convert = simple_event_to_convert.copy()
        if hasattr(simple_event_to_convert, "pitch_list") and (
            pl := simple_event_to_convert.pitch_list
        ):
            if len(pl) > 1:
                min_pitch, max_pitch = min(pl), max(pl)
                i0, i1 = (
                    self.scale.pitch_tuple.index(p) for p in (min_pitch, max_pitch)
                )
                new_pitch_list = []
                for i in range(i0, i1 + 1):
                    new_pitch_list.append(self.scale.pitch_tuple[i])
                simple_event_to_convert = simple_event_to_convert.set(
                    "pitch_list", new_pitch_list
                )
            else:
                warnings.warn("Cluster with only one pitch detected!")
        else:
            warnings.warn("Cluster without pitch list!")
        sequential_event.append(simple_event_to_convert)
        return sequential_event

    @property
    def playing_indicator_name(self) -> str:
        return "cluster"

    @property
    def default_playing_indicator(self) -> music_parameters.abc.PlayingIndicator:
        return music_parameters.abc.ExplicitPlayingIndicator()


class FlageoletConverter(music_converters.PlayingIndicatorConverter):
    def __init__(
        self,
        simple_event_to_playing_indicator_collection: typing.Callable[
            [core_events.SimpleEvent],
            music_parameters.PlayingIndicatorCollection,
        ] = music_converters.SimpleEventToPlayingIndicatorCollection(),
    ):
        super().__init__(simple_event_to_playing_indicator_collection)

    def _apply_playing_indicator(
        self,
        simple_event_to_convert: core_events.SimpleEvent,
        playing_indicator: music_parameters.abc.ExplicitPlayingIndicator,
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        sequential_event = core_events.SequentialEvent([])
        simple_event_to_convert = simple_event_to_convert.copy()
        if simple_event_to_convert.pitch_list:
            simple_event_to_convert.pitch_list[
                0
            ] += music_parameters.JustIntonationPitch("2/1")
        sequential_event.append(simple_event_to_convert)
        return sequential_event

    @property
    def playing_indicator_name(self) -> str:
        return "flageolet"

    @property
    def default_playing_indicator(self) -> music_parameters.abc.PlayingIndicator:
        return music_parameters.abc.ExplicitPlayingIndicator()


class BendAfterConverter(music_converters.PlayingIndicatorConverter):
    def __init__(
        self,
        simple_event_to_playing_indicator_collection: typing.Callable[
            [core_events.SimpleEvent],
            music_parameters.PlayingIndicatorCollection,
        ] = music_converters.SimpleEventToPlayingIndicatorCollection(),
    ):
        super().__init__(simple_event_to_playing_indicator_collection)

    def _apply_playing_indicator(
        self,
        simple_event_to_convert: core_events.SimpleEvent,
        playing_indicator: music_parameters.BendAfter,
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        sequential_event = core_events.SequentialEvent([])
        simple_event_to_convert = simple_event_to_convert.copy()
        if playing_indicator.bend_amount > 0:
            i = music_parameters.DirectPitchInterval(50)
        else:
            i = music_parameters.DirectPitchInterval(-50)
        for p in simple_event_to_convert.pitch_list:
            p.envelope = [
                [0, music_parameters.DirectPitchInterval(0)],
                [
                    simple_event_to_convert.duration * 0.5,
                    music_parameters.DirectPitchInterval(0),
                ],
                [simple_event_to_convert.duration, i],
            ]
        sequential_event.append(simple_event_to_convert)
        return sequential_event

    @property
    def playing_indicator_name(self) -> str:
        return "bend_after"

    @property
    def default_playing_indicator(self) -> music_parameters.abc.PlayingIndicator:
        return music_parameters.BendAfter()


class BridgeConverter(music_converters.PlayingIndicatorConverter):
    def _apply_playing_indicator(
        self,
        simple_event_to_convert: core_events.SimpleEvent,
        playing_indicator: music_parameters.abc.ExplicitPlayingIndicator,
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        sequential_event = core_events.SequentialEvent([])
        if not hasattr(simple_event_to_convert, "pitch_list"):
            simple_event_to_convert = music_events.NoteLike(
                duration=simple_event_to_convert.duration
            )
        else:
            simple_event_to_convert = simple_event_to_convert.copy()
        simple_event_to_convert.pitch_list = music_parameters.WesternPitch("c", 0)
        sequential_event.append(simple_event_to_convert)
        return sequential_event

    @property
    def playing_indicator_name(self) -> str:
        return "bridge"

    @property
    def default_playing_indicator(self) -> music_parameters.abc.PlayingIndicator:
        return music_parameters.abc.ExplicitPlayingIndicator()


class MovingOverpressureConverter(music_converters.PlayingIndicatorConverter):
    def _apply_playing_indicator(
        self,
        simple_event_to_convert: core_events.SimpleEvent,
        playing_indicator: music_parameters.abc.ExplicitPlayingIndicator,
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        sequential_event = core_events.SequentialEvent([])
        if not hasattr(simple_event_to_convert, "pitch_list"):
            simple_event_to_convert = music_events.NoteLike(
                duration=simple_event_to_convert.duration
            )
        else:
            simple_event_to_convert = simple_event_to_convert.copy()
        simple_event_to_convert.pitch_list = music_parameters.WesternPitch("cs", 0)
        sequential_event.append(simple_event_to_convert)
        return sequential_event

    @property
    def playing_indicator_name(self) -> str:
        return "moving_overpressure"

    @property
    def default_playing_indicator(self) -> music_parameters.abc.PlayingIndicator:
        return music_parameters.abc.ExplicitPlayingIndicator()


class BowedBoxConverter(music_converters.PlayingIndicatorConverter):
    def _apply_playing_indicator(
        self,
        simple_event_to_convert: core_events.SimpleEvent,
        playing_indicator: music_parameters.abc.ExplicitPlayingIndicator,
    ) -> core_events.SequentialEvent[core_events.SimpleEvent]:
        sequential_event = core_events.SequentialEvent([])
        if not hasattr(simple_event_to_convert, "pitch_list"):
            simple_event_to_convert = music_events.NoteLike(
                duration=simple_event_to_convert.duration
            )
        else:
            simple_event_to_convert = simple_event_to_convert.copy()
        simple_event_to_convert.pitch_list = music_parameters.WesternPitch("c", 0)
        sequential_event.append(simple_event_to_convert)
        return sequential_event

    @property
    def playing_indicator_name(self) -> str:
        return "bowed_box"

    @property
    def default_playing_indicator(self) -> music_parameters.abc.PlayingIndicator:
        return music_parameters.abc.ExplicitPlayingIndicator()
