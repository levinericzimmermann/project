% Draw a string instrument body instead of a normal clef.
% (see "Lachenmann Pression" for reference)

#(define make-bridge-path
    (lambda
        (
            ; general variables
            x-offset
            y-offset
            scale
            ;
            ; string variables
            string-distance
            string-length
            ;
            ; frog variables
            frog-length
            frog-string-overlap-x
            frog-string-overlap-y
            frog-small-length
            ;
            ; fretboard variables
            fretboard-length
            fretboard-string-overlap-x
            fretboard-string-overlap-y
            fretboard-small-length
            ;
            ; bridge variables
            bridge-height
        )
        (letrec* (
                ; string data
                (string-0-x x-offset)
                (string-1-x (+ string-0-x string-distance))
                (string-2-x (+ string-1-x string-distance))
                (string-3-x (+ string-2-x string-distance))
                (y-end (+ y-offset string-length))
                ;
                ; frog data
                (frog-x-0-0 (- string-0-x frog-string-overlap-x))
                (frog-x-0-1 (+ string-3-x frog-string-overlap-x))
                (frog-length-0 (- frog-x-0-1 frog-x-0-0))
                (frog-small-length-difference (/ (- frog-length-0 frog-small-length) 2))
                (frog-x-1-0 (+ frog-x-0-0 frog-small-length-difference))
                (frog-x-1-1 (+ frog-x-1-0 frog-small-length))
                (frog-y-0 (- y-end frog-string-overlap-y))
                (frog-y-1 (+ frog-y-0 frog-length))
                ;
                ; fretboard data
                (fretboard-x-0-0 (- string-0-x fretboard-string-overlap-x))
                (fretboard-x-0-1 (+ string-3-x fretboard-string-overlap-x))
                (fretboard-length-0 (- fretboard-x-0-1 fretboard-x-0-0))
                (fretboard-small-length-difference (/ (- fretboard-length-0 fretboard-small-length) 2))
                (fretboard-x-1-0 (+ fretboard-x-0-0 fretboard-small-length-difference))
                (fretboard-x-1-1 (+ fretboard-x-1-0 fretboard-small-length))
                (fretboard-y-0 (- y-offset fretboard-string-overlap-y))
                (fretboard-y-1 (+ fretboard-y-0 fretboard-length))
                ;
                ; bridge data
            )
                (list
                    ; First create string lines
                    (list 'moveto string-0-x y-offset)
                    (list 'lineto string-0-x y-end)
                    (list 'moveto string-1-x y-offset)
                    (list 'lineto string-1-x y-end)
                    (list 'moveto string-2-x y-offset)
                    (list 'lineto string-2-x y-end)
                    (list 'moveto string-3-x y-offset)
                    (list 'lineto string-3-x y-end)
                    ;
                    ; Next we draw the frog
                    (list 'moveto frog-x-0-0 frog-y-0)
                    (list 'lineto frog-x-0-1 frog-y-0)
                    (list 'lineto frog-x-1-1 frog-y-1)
                    (list 'moveto frog-x-1-0 frog-y-1)
                    (list 'lineto frog-x-0-0 frog-y-0)
                    ;
                    ; Next we draw the fretboard
                    (list 'moveto fretboard-x-1-0 fretboard-y-0)
                    (list 'moveto fretboard-x-1-1 fretboard-y-0)
                    (list 'lineto fretboard-x-0-1 fretboard-y-1)
                    (list 'lineto fretboard-x-0-0 fretboard-y-1)
                    (list 'lineto fretboard-x-1-0 fretboard-y-0)
                    ;
                    ; Finally we draw the bridge
                    (list 'moveto 0 0)
                    (list 'curveto 0 0 (/ string-3-x 2) bridge-height string-3-x 0)
                )
        )
    )
)

bridge-path = #(
    make-bridge-path
        ; general
        0 -7 1
        ; strings
        1.1 9.5
        ; frog
        4 1 1 3
        ; fretboard
        7 1 2 4
        ; bridge
        1.25
)

bridgeClef = {
    \override Staff.Clef.stencil = #ly:text-interface::print
    \override Staff.Clef.text = \markup {
        \scale #'(0.6 . 0.6)
        \path #0.2 #bridge-path
    }
}
