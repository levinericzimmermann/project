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
    "kug-to-crossing",
    "crossing-to-park",
    "park-to-cathedral-to-organ-institute",
    "organ-institute-to-schlossberg",
    "schlossberg-to-mur",
    "mur-to-tunnel",
    "tunnel-to-light",
)

j = music_parameters.JustIntonationPitch

# we have the following limitations:
# (all measured \w a'=442Hz)
#
#   brendans diy aluminium metal:
#
#       g   -40ct   => 7/4
#       f   +37ct   => 13/8
#       f#  +18ct   => 17/10
#
#
#   prayer bowls:
#
#       e   -30ct   => 119/96 (17/16 + 7/6)
#       g   -17ct   => 16/9 (13ct off)
#       f#  -35ct   => 105/64 (8ct off) (15/8 + 7/4)
#       a   -40ct   => 63/64 (10ct off) (7/4 + 9/8)
#
PART_TUPLE = (
    # kug -> crossing
    #   kug leaving:                just fifth (same like the end)
    #   crossing:                   dominant major
    ((j("35/24"), j("35/32")), (j("105/64"), j("45/32"), j("35/32"))),
    # crossing -> park
    # we walk with prayer bowl f#-35ct (= 105/64) prayer bowl
    #   crossing:                   ?
    #   park:                       ?
    ((j("105/64"), j("45/32"), j("35/32")), (j("105/64"), j("21/16"), j("7/4"))),
    # park -> cathedral -> organ institute
    # we walk with prayer bowl a-40 ct (= 63/64)
    #   park leaving:               ?   vielleicht a' prayer bowl? das ist wie ein 9/8 zu brendans g'
    #   cathedral:                  g -40ct, f +37ct, f# +18ct (brendans tuning)
    #   organ institute arrival:    c-major (alyssas tuning)
    (
        (j("21/16"), j("63/64"), j("7/4")),
        # f#+18      f+37       g-40 (-30)
        (j("17/10"), j("13/8"), j("7/4")),
        # c-major alyssa
        (j("32/27"), j("16/9"), j("40/27")),
    ),
    # organ institute -> schlossberg
    # we walk with 4 x harmonica
    #   organ leaving:              as-major
    #   schlossberg arrival:        c-major/g-major (harmonica tuning)
    (
        (j("32/27"), j("64/45"), j("256/135")),
        (j("3/2"), j("1/1")),
        (j("1/1"), j("3/4"), j("5/4")),
        (j("3/2"), j("15/8"), j("5/4")),
    ),
    # schlossberg -> mur
    # we walk with prayer bowl e-30ct (17/16 + 7/6)
    #   schlossberg:                we make a similar harmony as before,
    #                                   but everything moved by 17/16
    #   mur:                        we make a similar harmony as later,
    #                                   but everything moved by 17/16
    (
        (j("3/2") + j('17/16'), j("7/4") + j('17/16'), j("7/6") + j('17/16')),
        (j("16/9") + j("17/16"), j("4/3") + j("17/16"), j("7/6") + j("17/16")),
    ),
    # mur -> tunnel
    # we walk with prayer bowl g-17 ct (~16/9)
    #   mur:                        some harmony around 16/9
    #   tunnel:                     a harmonics, but with 16/9 (due to prayer bowl)
    ((j("16/9"), j("4/3"), j("7/6")), (j("1/1"), j("3/2"), j("16/9"))),
    # tunnel -> light
    #   tunnel:                     a harmonics
    #   light:                      a + e, just fifth interval
    ((j("1/1"), j("3/2"), j("5/4")), (j("1/1"), j("3/2"))),
)

DURATION_TUPLE = (
    # kug -> crossing
    3 * 60,
    # crossing -> park
    3 * 60,
    # park -> cathedral -> organ institute
    10 * 60,
    # organ institute -> schlossberg
    15 * 60,
    # schlossberg -> mur
    10 * 60,
    # mur -> tunnel
    5 * 60,
    # tunnel -> light
    3 * 60,
)


# sanity checks
assert len(DURATION_TUPLE) == len(PART_TUPLE)
assert len(DURATION_TUPLE) == len(PATH_TUPLE)

del j
