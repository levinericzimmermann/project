#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mutwo import music_parameters
import project

print("This prints how to tune the tuning forks in order to play")
print("the piece 11.1.")
print("")

# The actual concert pitch is not the a=442, but the G, which is our 1/1
# (because it's not possible to tune tuning forks lower). But in most
# electronic tuners, it is not possible to use such a low concert pitch.
# Therefore for tuning the forks we transpose everything here.
print("Concert pitch of a':\t", project.constants.A.frequency, "\n")

for i, fork in enumerate(project.constants.TUNING_FORK_TUPLE):
    fork = fork - music_parameters.JustIntonationPitch("8/7")
    print(
        i + 1,
        "\t",
        fork.get_closest_pythagorean_pitch_name("a"),
        "\t",
        fork.cent_deviation_from_closest_western_pitch_class,
    )
