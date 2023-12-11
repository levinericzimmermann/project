from mutwo import music_parameters

j = music_parameters.JustIntonationPitch

# Tuner concert pitch
A = music_parameters.DirectPitch(442)

# We use g' as the concert pitch, because with magnets it's only possible to
# tune tuning forks lower but not higher and most tuning forks are in a'.
# Therefore our 1/1 can't be a', but needs to be g (major second = 7/8 below
# the pitch a').
music_parameters.configurations.DEFAULT_CONCERT_PITCH = (A - j("8/7")).frequency


TUNING_FORK_TUPLE = (
    j("7/8"),
    j("11/12"),
    j("21/22"),
    j("1/1"),
    j("22/21"),
    j("12/11"),
    j("8/7"),
)

del j
