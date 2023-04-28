# Wait for mutwo.music fix! ( commit 2f2883adb390493912e6157f3dc00af2f14d9b2a )

from __future__ import annotations

import dataclasses
import functools
import typing

from mutwo import music_parameters

if 1:

    @property
    def harmonic_pitch_ambitus(self) -> music_parameters.abc.PitchAmbitus:
        """Get flageolet :class:`music_parameters.abc.PitchAmbitus`."""
        hp_tuple = self.harmonic_pitch_tuple
        return music_parameters.OctaveAmbitus(hp_tuple[0], hp_tuple[-1])

    music_parameters.StringInstrumentMixin.harmonic_pitch_ambitus = (
        harmonic_pitch_ambitus
    )


@dataclasses.dataclass(frozen=True)
class String(object):
    """:class:`String` represents a string of an instrument.

    :param index: The index of a :class:`String`. This is important
        in order to differentiate how far two strings are from
        each other.
    :type index: int
    :param tuning: The pitch to which the string is tuned to.
    :type tuning: music_parameters.abc.Pitch
    :param tuning_original: If the standard tuning of a string
        differs from its current tuning (e.g. if a scordatura
        is used) this parameter can be set to the standard tuning.
        This is useful in case one wants to notate the fingering
        of a harmonic and not the sounding result. The ``pitch``
        attribute of :class:`NaturalHarmonic.Node` uses `tuning_original`
        for calculation instead of `tuning. If `tuning_original`
        is ``None`` it is auto-set to `tuning`. Default to ``None``.
    :type tuning_original: typing.Optional[music_parameters.abc.Pitch]
    :param max_natural_harmonic_index: Although we can imagine infinite
        number of natural harmonics, in the real world it's not so
        easy to play higher flageolet. It's therefore a good idea
        to denote a limit of the highest natural harmonic. This
        limit defines the highest :class:`NaturalHarmonic` which is
        returned when accessing :class:`String`s
        ``natural_harmonic_tuple`` property. No matter what is
        set to ``max_natural_harmonic_index``, you can still get
        infinitely high :class:`NaturalHarmonic` of a :class:`String`
        with its ``index_to_natural_harmonic`` method. Default to 6.
    :type max_natural_harmonic_index: int

    **Example:**

    >>> from mutwo import music_parameters
    >>> g_string = music_parameters.String(0, music_parameters.WesternPitch('g', 3))
    >>> g_string
    String(WesternPitch('g', 3))
    >>> retuned_g_string = music_parameters.String(
    ...     0,
    ...     music_parameters.WesternPitch('g', 3),
    ...     tuning_original=music_parameters.JustIntonationPitch('8/11'),
    ... )
    >>> retuned_g_string
    String(WesternPitch('g', 3))
    """

    index: int
    tuning: music_parameters.abc.Pitch
    tuning_original: typing.Optional[music_parameters.abc.Pitch] = None
    max_natural_harmonic_index: int = 6

    def __post_init__(self):
        object.__setattr__(self, "tuning_original", self.tuning_original or self.tuning)
        object.__setattr__(self, "_index_to_natural_harmonic", {})

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.tuning})"

    @functools.cached_property
    def natural_harmonic_tuple(self) -> tuple[music_parameters.NaturalHarmonic, ...]:
        """All :class:`NaturalHarmonic` with index from 2 until ``max_natural_harmonic_index``."""
        return tuple(
            (
                self.index_to_natural_harmonic(i)
                for i in range(2, self.max_natural_harmonic_index + 1)
            )
        )

    def index_to_natural_harmonic(
        self, natural_harmonic_index: int
    ) -> music_parameters.NaturalHarmonic:
        """Find natural harmonic with given partial index.

        :param natural_harmonic_index: The partial index; e.g. 2 is the first
            overtone (an octave above the root), 3 the second overtone (octave
            plus fifth), etc.
        :type natural_harmonic_index: int

        **Example:**

        >>> from mutwo import music_parameters
        >>> g_string = music_parameters.String(
        ...     0, music_parameters.WesternPitch('g', 3)
        ... )
        >>> g_string.index_to_natural_harmonic(5)
        NaturalHarmonic(index=5, tonality=True)
        """
        try:
            return self._index_to_natural_harmonic[natural_harmonic_index]
        except KeyError:
            h = self._index_to_natural_harmonic[
                natural_harmonic_index
            ] = music_parameters.NaturalHarmonic(natural_harmonic_index, self)
            return h


music_parameters.String = String


if 1:

    # Fix for proper representation of scales (e.g. taking into account western
    # pitch interval, so a major sixth above a is f# and not gf).
    #
    # mutwo.music doesn't implement its own __add__ or __sub__ yet and
    # then we simply get DirectPitchInterval which don't know anything about
    # proper pitch class names.

    def WesternPitchInterval__add__(self, other: music_parameters.abc.PitchInterval):
        if isinstance(other, music_parameters.WesternPitchInterval):
            match other.name:
                case "p8":
                    if not self.is_interval_falling:
                        return music_parameters.WesternPitchInterval(
                            f"{self.interval_quality}{int(self.interval_type) + 7}"
                        )
                case "p-8":
                    if self.is_interval_falling:
                        return music_parameters.WesternPitchInterval(
                            f"{self.interval_quality}-{int(self.interval_type) + 7}"
                        )
                    else:
                        match self.interval_quality:
                            case "M":
                                interval_quality = "m"
                            case "m":
                                interval_quality = "M"
                            case "p":
                                interval_quality = "p"
                            case _:
                                interval_quality = None
                        match int(self.interval_type):
                            case 1:
                                interval_type = 8
                            case 2:
                                interval_type = 7
                            case 3:
                                interval_type = 6
                            case 4:
                                interval_type = 5
                            case 5:
                                interval_type = 4
                            case 6:
                                interval_type = 3
                            case 7:
                                interval_type = 2
                            case _:
                                interval_type = None
                        if interval_quality and interval_type:
                            return music_parameters.WesternPitchInterval(
                                f"{interval_quality}-{int(interval_type)}"
                            )
                case _:
                    pass

        return music_parameters.abc.PitchInterval.__add__(self, other)

    music_parameters.WesternPitchInterval.__add__ = WesternPitchInterval__add__
