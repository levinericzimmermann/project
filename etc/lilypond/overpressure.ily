overpressurePath = #'(
    (moveto 0 2)
    (lineto 2 -0.5)
    (moveto 2.9 -0.5)
    (lineto 3.75 1.55)
    (moveto 5 2)
    (lineto 6 1)
    (lineto 8 1.85)
    (curveto 8 2 9 -0.25 11 1.5)
    (moveto 12 -0.4)
    (lineto 13 0.25)
)


drawOverpressurePath = #(define-music-function () ()
       #{
          _ \markup {
            \path #0.5 #overpressurePath
          }
       #}
)
