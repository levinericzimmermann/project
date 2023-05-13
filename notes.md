## Cello/Viola


    C   7/6
    G   16/9
    D   4/3
    A   64/63


C-Saite

    C       7/6     32/21       16/9
    C       32/27   3/2         16/9
    D       4/3     4/3         16/9
    E       3/2     32/27       16/9
    F       14/9    8/7         16/9
    G       16/9    1/1         16/9


G-Saite (mit C-Saite)

    G       7/6     32/21       16/9
    A       7/6     12/7        2/1
    # C       7/6     2/1         7/3


G-Saite (mit D-Saite)

    # G       16/9    3/2         4/3
    A       2/1     4/3         4/3
    B       9/8     4/3         3/2
    C       7/6     8/7         4/3
    D       4/3     1/1         4/3


D-Saite (mit G-Saite)

    D       16/9    3/2         4/3


D-Saite (mit A-Saite)

    # E       4/3         32/21       64/63
    # E       256/189     3/2         64/63
    # F#      256/147     7/6         64/63
    # G       16/9        8/7         64/63

    E       4/3         3/2         2/1
    F#      12/7        7/6         2/1
    G       16/9        9/8         2/1
    A       2/1         1/1         2/1


A-Saite

    A       4/3         3/2         2/1
    B       4/3                     9/8
    C       4/3         12/7        7/6
    D       4/3         2/1         4/3



=> it's better if we tune the A string to 1/1 indeed.

How to encode this?

    scale_degree (which it represents)
    main string,        side string
    main string pitch,  side string pitch (if default it's the strings pitch)

        stable? => whether it's a 'good' C or a 'bad' C
                => perhaps this can be a @property, can be
                   figured out from global scale :)

---

Maybe all those fancy tuning ideas aren't necessary for the cello/viola?

Currently I feel it would fit better, if the cello/viola sounds are always damped and weak,
and if there is never a strong brilliant sound.

But maybe this is possible, and then we still can have few moment where the
cello works very different and actually does provide some more moving sounds?


---


C G D A


Es gibt 6 verschiedene Doppelgriffe:

    (wenn immer eine Saite offen bleiben soll)
    (grosser Buchstabe fuer gedrueckte Saite, kleiner Buchstabe fuer offene Saite)


    1   C g
    2   c G
    3     G d
    4     g D
    5       D a
    6       d A


Wenn wir nur 2-5 nehmen, muessen die auesseren Saiten nie gegriffen werden:

    2   c G
    3     G d
    4     g D
    5       D a


Von 6 kann sich nur zu 5 bewegt werden, von 5 zu 6 oder zu 4, usw.
Die Intervalle zwischen den beiden Saiten muessen immer stimmbar sein (nach Sabat Tabelle).

    Vielleicht kannst du es sogar noch explizit einfacher machen,
    und nur einfach stimmbare Intervalle schreiben,
    und Abweichungen entstehen immer nur ueber verstimmte Saiten.


c       =       7/6
g       =       16/9
d       =       4/3
a       =       1/1


Alternative:

        =       16/9
        =       12/7
        =       7/6
        =       9/8


-3 -2 -1 0 +1 +2 +3


+2 +3 -3 -2 als "schlechte Quintenkette" benutzen?


        C           G               Df          Af

=>      9/8         12/7            7/6         16/9

               729          533            729



=> Bf ist dann 1/1
=> normal gestimmte Saiten sind besser zu greifen?
=> nur die "C" Saite ist hier relativ normal :(



Alternativ:

    4/3     1/1     3/2     9/8

    1/1     3/2     9/8     12/7



-----------




- glockenspiel kann gleiche skala haben:
    - b und e werden nicht hoeher gestimmt und sind deshalb leicht verstimmt
    - f# wird auch nicht umgestimmt: das hat dann 27/16, also pythagoraeisches intervall
    - die funktion des f# ist aber dieselbe
    - dh. bei f# bekommen wir dann immer gewisse reibungen
    - dh. f# sollte vermutlich nicht der grundton sein!
