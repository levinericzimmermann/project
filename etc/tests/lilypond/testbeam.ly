\version "2.24.1"
\include "etc/lilypond/ar.ily"

\score {

    \new Voice {
        \Acc #8
        c'8
        s8
        \Rit #8
        c'8
        s8
        \RitAcc #8
        c'8
        \AccRit #8
        c'8
    }

}
