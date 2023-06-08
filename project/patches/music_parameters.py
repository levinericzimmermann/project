# Wait for mutwo.music fix! ( commit 2f2883adb390493912e6157f3dc00af2f14d9b2a )

from __future__ import annotations

import dataclasses
from mutwo import music_parameters


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
