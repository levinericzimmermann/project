sr     = 44100
ksmps  = 1
0dbfs  = 1
nchnls = 1

instr 1
    iDuration = p3
    iAttack = iDuration * 0.4
    iReverb = iDuration * 0.4
    kenv linseg 0, iAttack, 1, iDuration - (iAttack + iReverb), 1, iReverb, 0
    asig poscil3 p5 * kenv, p4
    out asig
endin
