# Structure

## Form

- a sequence of slowly unfolding events, sounds
    - each breath matters

- composed of small parts
    - each part consist of:
        - N resonator-algorithms (where n >= 1)
        - whistling sequence
        - resonator result (concurrence, that may be longer than the actual part, e.g resonators can overlap)
    - harmonic: can be stabilizing or move further
        - we can divide entries into 'stable' and 'unstable'
        - if moving, we may even hint at which direction the harmony is moving:
            - 1/1
            - 3/2
            - ...
    - complexity of spectra
        - more consonsant sounds can have wider and more present spectra,
          than less tuneable / rather unstable sounds
    - volume:
        - same as complexity of spectra: complex sounds need more quietude

- there is a global intonation envelope, that keeps track of all sounding intonations
    - each part writes into this intonation envelope once it's used

- how to order parts? how do parts decide for pitches?


## Representation of musical material / breath

Each musical part is a ``SimultaneousEvent`` that contains N voices.
The first voice must be the breath voice.
This is a SequentialEvent[BreathEvent], where each breath event has
a duration of 1 and has a value which tells what type of breath is done:

    - inhale (slow or fast)
    - exahle (slow or fast)
    - holding breath

All other voices assume that the duration of 1 equals one breath part.
So the duration inside the voices doesn't reflect the 'real' duration,
but the duration according to the breath sequence.

## Harmony

harmony is based on a set of tuning forks.
each tuning fork represents a valid tonic, between these
tonics the music switching.
