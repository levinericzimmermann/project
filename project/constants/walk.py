from mutwo import music_parameters


PEOPLE_TUPLE = (
    "alyssa",
    "kevin",
    "juro",
    "eden",
    "levin",
    "brendan",
    "manuel",
    "maxime",
    "parza",
    "roman",
    "jieun",
)

PATH_TUPLE = (
    "kup-to-crossing",
    "crossing-to-park",
    "park-to-cathetral-to-organ-institute",
    "organ-institute-to-schlossberg",
    "schlossberg-to-mur",
    "mur-to-tunnel",
    "tunnel-to-light",
)

j = music_parameters.JustIntonationPitch
PART_TUPLE = (
    # kup -> crossing
    #   kup leaving:                ?
    #   crossing:                   ?
    ((j("1/1"), j("3/4"), j("7/6")), (j("1/1"), j("2/3"), j("9/8"))),
    # crossing -> park
    #   crossing:                   ?
    #   park:                       ?
    ((j("1/1"), j("3/4"), j("7/6")), (j("1/1"), j("2/3"), j("9/8"))),
    # park -> cathetral -> organ institute
    #   park leaving:               ?
    #   cathertal:                  ?
    #   organ institute arrival:    c-major
    ((j("1/1"), j("3/4"), j("7/6")), (j("5/4"), j("25/16"), j("15/8"))),
    # organ institute -> schlossberg
    #   organ leaving:              as-major
    #   schlossberg arrival:        ?
    ((j("16/15"), j("4/3"), j("8/5")), (j("5/4"), j("25/16"), j("15/8"))),
    # schlossberg -> mur
    #   schlossberg:                ?
    #   mur:                        ?
    ((j("1/1"), j("3/4"), j("7/6")), (j("1/1"), j("2/3"), j("9/8"))),
    # mur -> tunnel
    #   mur:                        ?
    #   tunnel:                     ?
    ((j("1/1"), j("3/4"), j("7/6")), (j("1/1"), j("2/3"), j("9/8"))),
    # tunnel -> light
    #   tunnel:                     ?
    #   light:                      ?
    ((j("1/1"), j("3/4"), j("7/6")), (j("1/1"), j("2/3"), j("9/8"))),
)

DURATION_TUPLE = (
    5 * 60,
    5 * 60,
    5 * 60,
    5 * 60,
    5 * 60,
    5 * 60,
    5 * 60,
)


# sanity checks
assert len(DURATION_TUPLE) == len(PART_TUPLE)
assert len(DURATION_TUPLE) == len(PATH_TUPLE)

del j
