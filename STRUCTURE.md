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

Harmony is based on a set of tuning forks.
Each tuning fork represents a valid tonic, between these
tonics the music is switching.

## Sections

Maybe various sections could be beautiful.
So that's really more like a collection, a song-book,
than a composition. More a list of possibilities than
a master-work. More options than settlements.

## Order and freedom

Does the form really needs to be fixed e.g. does the linear order
really has to be in the way how it is?

In fact we have entries and they are sorted.

They are repeated and varied.

Couldn't it be enough to provide the various entries and the
player can go through them ad. libitum (or according to allowed
path)?

So the page is more a sequence of allowed entries, the player
can go through.

Think of Feldmans Intersection.
Think of a real meditative exercise.
Think about the fact that music is not exactly linear.

How should they be sorted on the page?

How should the modulations happens?

    The linearity indeed has a lot of connections to
    modulations. Modulations need linearity, because
    we need to prepare and anticipate them and
    after-reflect on them.

How should the patch work?

    Because here we also really have the problem
    that in walkman cues are sorted linearly, it's
    not a grid or a landscape. So for this we would
    perhaps really need wm2 or something completely
    different.

Imagine a page for each tuning fork, for each tonic.

    Maybe therefore the pages need to hang?
    Or yes, it's maybe more a sculpture than a book.


A strong argument for linearity is the fact
that breathing is linear. It doesn't stop.
Never. Therefore there is no 'space' between
entries. Not like Feldmans intersection. No
space. Just continuity. *Continuous breathing*.


