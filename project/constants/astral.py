from mutwo import music_parameters
from mutwo import project_parameters

j = music_parameters.JustIntonationPitch
mp = project_parameters.MoonPhase
sl = project_parameters.SunLight
ml = project_parameters.MoonLight

MOON_PHASE_TO_INTONATION = {
    mp.NEW: (
        j("1/1"),
        j("9/8"),
        j("32/27"),
        j("4/3"),
        j("3/2"),
        j("27/16"),
        j("16/9"),
    ),
    mp.WAXING_CRESCENT: (
        j("1/1"),
        j("9/8"),
        j("7/6"),
        j("4/3"),
        j("3/2"),
        j("12/7"),
        j("16/9"),
    ),
    mp.QUARTER_0: (
        j("1/1"),
        j("9/8"),
        j("32/27"),
        j("4/3"),
        j("3/2"),
        j("27/16"),
        j("16/9"),
    ),
    mp.WAXING_GIBBOUS: (
        j("1/1"),
        j("9/8"),
        j("32/27"),
        j("4/3"),
        j("3/2"),
        j("27/16"),
        j("16/9"),
    ),
    mp.FULL: (
        j("1/1"),
        j("9/8"),
        j("32/27"),
        j("4/3"),
        j("3/2"),
        j("27/16"),
        j("16/9"),
    ),
    mp.WANING_GIBBOUS: (
        j("1/1"),
        j("9/8"),
        j("32/27"),
        j("4/3"),
        j("3/2"),
        j("27/16"),
        j("16/9"),
    ),
    mp.QUARTER_1: (
        j("1/1"),
        j("9/8"),
        j("32/27"),
        j("4/3"),
        j("3/2"),
        j("27/16"),
        j("16/9"),
    ),
    mp.WANING_CRESCENT: (
        j("1/1"),
        j("9/8"),
        j("32/27"),
        j("4/3"),
        j("3/2"),
        j("27/16"),
        j("16/9"),
    ),
}

SUN_LIGHT_TO_PITCH_TUPLE = {
    sl.MORNING_TWILIGHT: (j("1/1"), j("9/8"), j("32/27"), j("4/3"), j("3/2")),
    sl.DAYLIGHT: (j("1/1"), j("9/8"), j("32/27"), j("4/3"), j("3/2")),
    sl.EVENING_TWILIGHT: (j("1/1"), j("9/8"), j("32/27"), j("4/3"), j("3/2")),
    sl.NIGHTLIGHT: (j("1/1"), j("9/8"), j("32/27"), j("4/3"), j("3/2")),
}

MOON_LIGHT_TO_PITCH_TUPLE = {
    ml.ABSENT: (j("1/1"), j("32/27"), j("4/3")),
    ml.PRESENT: (j("1/1"), j("32/27"), j("3/2")),
}

del j, mp
