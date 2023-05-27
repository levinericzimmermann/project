syncPath = #'(
    (moveto 0.5 -1.5)
    (lineto 0.5 -1.6)
    (moveto 0.5 -2)
    (lineto 0.5 -2.1)
    (moveto 0.5 -2.5)
    (lineto 0.5 -2.6)
    (moveto 0.5 -3)
    (lineto 0.5 -3.1)
    (moveto 0.5 -3.5)
    (lineto 0.5 -3.6)
    (moveto 0.5 -4)
    (closepath)
)


drawSyncPath = #(define-music-function () ()
       #{
          _ \markup {
            \path #0.2 #syncPath
          }
       #}
)
