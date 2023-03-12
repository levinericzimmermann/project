from mutwo import music_parameters

DEFAULT_VIOLIN_DICT = dict(
    name="violin",
    short_name="vl.",
    pitch_ambitus=music_parameters.OctaveAmbitus(
        music_parameters.WesternPitch("g", 3),
        music_parameters.WesternPitch("e", 7),
    ),
    string_tuple=(
        music_parameters.String(
            0,
            music_parameters.JustIntonationPitch("4/9"),
            music_parameters.WesternPitch("g", 3),
        ),
        music_parameters.String(
            1,
            music_parameters.JustIntonationPitch("2/3"),
            music_parameters.WesternPitch("d", 4),
        ),
        music_parameters.String(
            2,
            music_parameters.JustIntonationPitch("1/1"),
            music_parameters.WesternPitch("a", 4),
        ),
        music_parameters.String(
            3,
            music_parameters.JustIntonationPitch("3/2"),
            music_parameters.WesternPitch("e", 5),
        ),
    ),
)

DEFAULT_CLAVICHORD_DICT = dict(
    name="clavichord",
    short_name="clav.",
)
