<CsoundSynthesizer>
<CsOptions>

-+rtaudio=jack
-odac
-iadc
-B 2048

</CsOptions>
<CsInstruments>

sr     = 48000
ksmps  = 32
nchnls = 4
0dbfs  = 1

instr 1

    aSignal0, aSignal1, aSignal2, aSignal3 inq

    fSignal0 pvsanal aSignal0, 1024, 256, 1024, 1
    fFilteredSignal0 pvstencil fSignal0, 0.1, 1, 1
    aFilteredSignal0 pvsynth fFilteredSignal0

    fSignal1 pvsanal aSignal1, 1024, 256, 1024, 1
    fFilteredSignal1 pvstencil fSignal1, 0.1, 1, 1
    aFilteredSignal1 pvsynth fFilteredSignal1

    fSignal2 pvsanal aSignal2, 1024, 256, 1024, 1
    fFilteredSignal2 pvstencil fSignal2, 0.1, 1, 1
    aFilteredSignal2 pvsynth fFilteredSignal2

    fSignal3 pvsanal aSignal3, 1024, 256, 1024, 1
    fFilteredSignal3 pvstencil fSignal3, 0.2, 0.85, 2
    aFilteredSignal3 pvsynth fFilteredSignal3

    outq  aFilteredSignal0, aFilteredSignal1, aFilteredSignal2, aFilteredSignal3

endin

</CsInstruments>
<CsScore>
f1 0 -1024 -43 "noise-48k.pvx" 0
f2 0 -1024 -43 "noise-guitar-48khz.pvx" 0
i 1 0 36000
</CsScore>
</CsoundSynthesizer>
