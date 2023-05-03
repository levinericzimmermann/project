#(define ar-distance -0.7)
#(define ar-thickness 0.3)

#(define make-path
    (lambda (start end factor offset ar-length)
        (let ((x-end (+ offset (* ar-length factor))))
            (list
                (list 'moveto offset 0)
                (list 'lineto x-end 0)
                (list 'moveto offset start)
                (list 'lineto x-end end)
            )
        )
    )
)

#(define make-rit-path (lambda (factor offset ar-length) (make-path ar-distance 0 factor offset ar-length)))
#(define make-acc-path (lambda (factor offset ar-length) (make-path 0 ar-distance factor offset ar-length)))

#(define rit-path
    (lambda (ar-length)
        (make-rit-path 1 0 ar-length)
    )
)

#(define acc-path
    (lambda (ar-length)
        (make-acc-path 1 0 ar-length)
    )
)

#(define rit-acc-path
    (lambda (ar-length)
        (append!
            (make-rit-path 0.5 0  ar-length)
            (make-acc-path 0.5 (* 0.5 ar-length)  ar-length)
        )
    )
)

#(define acc-rit-path
    (lambda (ar-length)
        (append!
            (make-acc-path 0.5 0  ar-length)
            (make-rit-path 0.5 (* 0.5 ar-length)  ar-length)
        )
    )
)

#(define ar-make-music-function
    (lambda (make-path)
        (define-music-function (ar-length) (number?)
            (let ((path (make-path ar-length)))
               #{
                  \stemUp
                  \once \override Staff.Flag.stencil = #ly:text-interface::print
                  \once \override Staff.Flag.text = \markup {
                    \path #ar-thickness #path
                  }
               #}
            )
        )
    )
)



Rit = #(ar-make-music-function rit-path)
Acc = #(ar-make-music-function acc-path)
RitAcc = #(ar-make-music-function rit-acc-path)
AccRit = #(ar-make-music-function acc-rit-path)

