%% This file is part of Ekmelily - Notation of microtonal music with LilyPond.
%% Copyright (C) 2013-2022  Thomas Richter <thomas-richter@aon.at>
%%
%% This program is free software: you can redistribute it and/or modify
%% it under the terms of the GNU General Public License as published by
%% the Free Software Foundation, either version 3 of the License, or
%% (at your option) any later version.
%%
%% This program is distributed in the hope that it will be useful,
%% but WITHOUT ANY WARRANTY; without even the implied warranty of
%% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%% GNU General Public License at <http://www.gnu.org/licenses/>
%% for more details.
%%
%%
%% File: ekmel-53.ily  -  Include file for the 53-EDO tuning
%% Latest revision: 28 June 2022
%%
%% This file is mainly intended for Turkish music based on the
%% Holdrian comma Hc = 1200 / 53
%%
%%
%% Sources:
%%
%% * M. Kemal Karaosmanoğlu:
%%   "A TURKISH MAKAM MUSIC SYMBOLIC DATABASE FOR MUSIC INFORMATION
%%   RETRIEVAL: SymbTr" (ISMIR 2012)
%%
%% * Makam note names are taken from turkish-makam.ly in LilyPond 2.22
%%   Copyright (C) 2019--2020 Adam Good <goodadamgood@gmail.com>
%%

\version "2.19.22"


% Makam alterations (cp. 72-edo and 1/9-tone)
#(define-public KOMA          6/53)  % c   1/12   1/9
#(define-public CEYREK        12/53) %     3/12
#(define-public EKSIK-BAKIYE  18/53) % eb  4/12   3/9
#(define-public BAKIYE        24/53) % b   5/12   4/9
#(define-public KUCUK         30/53) % k   6/12   5/9
#(define-public BUYUKMUCENNEB 48/53) % bm  10/12  8/9
#(define-public TANINI        60/53) % t   11/12  10/9


% Tuning table
ekmTuning = #'(
  (-1     0 54/53 108/53 132/53 186/53 240/53 294/53)
  (#x12 . 6/53)
  (#x16 . 12/53)
  (#x20 . 18/53)
  (#x24 . 24/53)
  (#x28 . 30/53)
  (#x2E . 36/53)
  (#x32 . 42/53)
  (#x3C . 48/53)
  (#x40 . 54/53)
  (#x44 . 60/53))


% Language tables
ekmLanguages = #'(

;; Makam names
(makam . (
  (c 0 . 0)
  (d 1 . 0)
  (e 2 . 0)
  (f 3 . 0)
  (g 4 . 0)
  (a 5 . 0)
  (b 6 . 0)

  (cc 0 . #x12)
  (dc 1 . #x12)
  (ec 2 . #x12)
  (fc 3 . #x12)
  (gc 4 . #x12)
  (ac 5 . #x12)
  (bc 6 . #x12)

  (cfc 0 . #x13)
  (dfc 1 . #x13)
  (efc 2 . #x13)
  (ffc 3 . #x13)
  (gfc 4 . #x13)
  (afc 5 . #x13)
  (bfc 6 . #x13)

  (ci 0 . #x16)
  (di 1 . #x16)
  (ei 2 . #x16)
  (fi 3 . #x16)
  (gi 4 . #x16)
  (ai 5 . #x16)
  (bi 6 . #x16)

  (cfi 0 . #x17)
  (dfi 1 . #x17)
  (efi 2 . #x17)
  (ffi 3 . #x17)
  (gfi 4 . #x17)
  (afi 5 . #x17)
  (bfi 6 . #x17)

  (ceb 0 . #x20)
  (deb 1 . #x20)
  (eeb 2 . #x20)
  (feb 3 . #x20)
  (geb 4 . #x20)
  (aeb 5 . #x20)
  (beb 6 . #x20)

  (cfu 0 . #x21)
  (dfu 1 . #x21)
  (efu 2 . #x21)
  (ffu 3 . #x21)
  (gfu 4 . #x21)
  (afu 5 . #x21)
  (bfu 6 . #x21)

  (cb 0 . #x24)
  (db 1 . #x24)
  (eb 2 . #x24)
  (fb 3 . #x24)
  (gb 4 . #x24)
  (ab 5 . #x24)
  (bb 6 . #x24)

  (cfb 0 . #x25)
  (dfb 1 . #x25)
  (efb 2 . #x25)
  (ffb 3 . #x25)
  (gfb 4 . #x25)
  (afb 5 . #x25)
  (bfb 6 . #x25)

  (ck 0 . #x28)
  (dk 1 . #x28)
  (ek 2 . #x28)
  (fk 3 . #x28)
  (gk 4 . #x28)
  (ak 5 . #x28)
  (bk 6 . #x28)

  (cfk 0 . #x29)
  (dfk 1 . #x29)
  (efk 2 . #x29)
  (ffk 3 . #x29)
  (gfk 4 . #x29)
  (afk 5 . #x29)
  (bfk 6 . #x29)

  (cbm 0 . #x3C)
  (dbm 1 . #x3C)
  (ebm 2 . #x3C)
  (fbm 3 . #x3C)
  (gbm 4 . #x3C)
  (abm 5 . #x3C)
  (bbm 6 . #x3C)

  (cfbm 0 . #x3D)
  (dfbm 1 . #x3D)
  (efbm 2 . #x3D)
  (ffbm 3 . #x3D)
  (gfbm 4 . #x3D)
  (afbm 5 . #x3D)
  (bfbm 6 . #x3D)

  (ct 0 . #x44)
  (dt 1 . #x44)
  (et 2 . #x44)
  (ft 3 . #x44)
  (gt 4 . #x44)
  (at 5 . #x44)
  (bt 6 . #x44)

  (cft 0 . #x45)
  (dft 1 . #x45)
  (eft 2 . #x45)
  (fft 3 . #x45)
  (gft 4 . #x45)
  (aft 5 . #x45)
  (bft 6 . #x45)))

;; THM (Turkish folk music) names
(thm . (
  (do 0 . 0)
  (do-s-three 0 . #x20)
  (re-b-four 1 . #x25)
  (re 1 . 0)
  (mi-b 2 . #x29)
  (mi-b-two 2 . #x17)
  (mi 2 . 0)
  (fa 3 . 0)
  (fa-s-three 3 . #x20)
  (sol-b-four 4 . #x25)
  (sol 4 . 0)
  (la-b 5 . #x29)
  (la-b-two 5 . #x17)
  (la 5 . 0)
  (si-b 6 . #x29)
  (si-b-two 6 . #x17)
  (si 6 . 0)))

;; KTM (Turkish classical music) names
(ktm . (
  (cargah 0 . 0)
  (nimhicaz 0 . #x24)
  (hicaz 0 . #x28)
  (dikhicaz 0 . #x3C)
  (yegah 1 . 0)
  (nimhisar 1 . #x24)
  (hisar 1 . #x28)
  (dikhisar 1 . #x3C)
  (huseyniasiran 2 . 0)
  (acemasiran 3 . 0)
  (dikacem 3 . #x12)
  (irak 3 . #x24)
  (gevest 3 . #x28)
  (dikgevest 3 . #x3C)
  (rast 4 . 0)
  (nimzirgule 4 . #x24)
  (zirgule 4 . #x28)
  (dikzirgule 4 . #x3C)
  (dugah 5 . 0)
  (kurdi 5 . #x24)
  (dikkurdi 5 . #x28)
  (segah 5 . #x3C)
  (buselik 6 . 0)
  (dikbuselik 0 . #x13)))

;; English names
(english . (
  (c 0 . 0)
  (d 1 . 0)
  (e 2 . 0)
  (f 3 . 0)
  (g 4 . 0)
  (a 5 . 0)
  (b 6 . 0)

  (cs 0 . #x12)
  (ds 1 . #x12)
  (es 2 . #x12)
  (fs 3 . #x12)
  (gs 4 . #x12)
  (as 5 . #x12)
  (bs 6 . #x12)

  (cf 0 . #x13)
  (df 1 . #x13)
  (ef 2 . #x13)
  (ff 3 . #x13)
  (gf 4 . #x13)
  (af 5 . #x13)
  (bf 6 . #x13)

  (cx 0 . #x16)
  (dx 1 . #x16)
  (ex 2 . #x16)
  (fx 3 . #x16)
  (gx 4 . #x16)
  (ax 5 . #x16)
  (bx 6 . #x16)

  (cff 0 . #x17)
  (dff 1 . #x17)
  (eff 2 . #x17)
  (fff 3 . #x17)
  (gff 4 . #x17)
  (aff 5 . #x17)
  (bff 6 . #x17)

  (csx 0 . #x20)
  (dsx 1 . #x20)
  (esx 2 . #x20)
  (fsx 3 . #x20)
  (gsx 4 . #x20)
  (asx 5 . #x20)
  (bsx 6 . #x20)

  (cfff 0 . #x21)
  (dfff 1 . #x21)
  (efff 2 . #x21)
  (ffff 3 . #x21)
  (gfff 4 . #x21)
  (afff 5 . #x21)
  (bfff 6 . #x21)

  (cxx 0 . #x24)
  (dxx 1 . #x24)
  (exx 2 . #x24)
  (fxx 3 . #x24)
  (gxx 4 . #x24)
  (axx 5 . #x24)
  (bxx 6 . #x24)

  (cffff 0 . #x25)
  (dffff 1 . #x25)
  (effff 2 . #x25)
  (fffff 3 . #x25)
  (gffff 4 . #x25)
  (affff 5 . #x25)
  (bffff 6 . #x25)))

;; English number names
(number . (
  (c 0 . 0)
  (d 1 . 0)
  (e 2 . 0)
  (f 3 . 0)
  (g 4 . 0)
  (a 5 . 0)
  (b 6 . 0)

  (cs-one 0 . #x12)
  (ds-one 1 . #x12)
  (es-one 2 . #x12)
  (fs-one 3 . #x12)
  (gs-one 4 . #x12)
  (as-one 5 . #x12)
  (bs-one 6 . #x12)

  (cb-one 0 . #x13)
  (db-one 1 . #x13)
  (eb-one 2 . #x13)
  (gb-one 4 . #x13)
  (ab-one 5 . #x13)
  (bb-one 6 . #x13)

  (cs-two 0 . #x16)
  (ds-two 1 . #x16)
  (es-two 2 . #x16)
  (fs-two 3 . #x16)
  (gs-two 4 . #x16)
  (as-two 5 . #x16)
  (bs-two 6 . #x16)

  (db-two 1 . #x17)
  (eb-two 2 . #x17)
  (gb-two 4 . #x17)
  (ab-two 5 . #x17)
  (bb-two 6 . #x17)

  (cs-three 0 . #x20)
  (ds-three 1 . #x20)
  (es-three 2 . #x20)
  (fs-three 3 . #x20)
  (gs-three 4 . #x20)
  (as-three 5 . #x20)

  (db-three 1 . #x21)
  (eb-three 2 . #x21)
  (gb-three 4 . #x21)
  (ab-three 5 . #x21)
  (bb-three 6 . #x21)

  (cs-four 0 . #x24)
  (ds-four 1 . #x24)
  (fs-four 3 . #x24)
  (gs-four 4 . #x24)
  (as-four 5 . #x24)

  (db-four 1 . #x25)
  (eb-four 2 . #x25)
  (gb-four 4 . #x25)
  (ab-four 5 . #x25)
  (bb-four 6 . #x25)))
)


% Notation tables
ekmNotations = #'(

;; AEU notation
(aeu . (
  (#x00 #xE261)
  (#x12 #xE444)
  (#x13 #xE443)
  (#x16)
  (#x17 #xF619)
  (#x20 #xE275)
  (#x21 #xF619)
  (#x24 #xE445)
  (#x25 #xE442)
  (#x28 #xE446)
  (#x29 #xE441)
  (#x2E)
  (#x2F)
  (#x32)
  (#x33)
  (#x3C #xE447)
  (#x3D #xE440)
  (#x40)
  (#x41)
  (#x44 #xED38)
  (#x45 #xED30)))

;; AEU notation with eksik-bakiye = koma (mirrored flat without slash)
(aeuek . (
  (#x00 #xE261)
  (#x12 #xE444)
  (#x13 #xE443)
  (#x16)
  (#x17 #xE443)
  (#x20 #xE275)
  (#x21 #xE443)
  (#x24 #xE445)
  (#x25 #xE442)
  (#x28 #xE446)
  (#x29 #xE441)
  (#x2E)
  (#x2F)
  (#x32)
  (#x33)
  (#x3C #xE447)
  (#x3D #xE440)
  (#x40)
  (#x41)
  (#x44 #xED38)
  (#x45 #xED30)))

;; THM notation
(thm . (
  (#x00 #xE261)
  (#x12 #xE450)
  (#x13 #xE454)
  (#x16 #xE451)
  (#x17 #xE455)
  (#x20 #xE452)
  (#x21 #xE456)
  (#x24 #xE445)
  (#x25 #xE457)
  (#x28 #xE453)
  (#x29 #xE441)
  (#x2E)
  (#x2F)
  (#x32)
  (#x33)
  (#x3C)
  (#x3D)
  (#x40)
  (#x41)
  (#x44)
  (#x45)))

;; Sagittal notation
(sag . (
  (#x00 #xE261)
  (#x12 #xE302)
  (#x13 #xE303)
  (#x16 #xE306)
  (#x17 #xE307)
  (#x20 #xE310)
  (#x21 #xE311)
  (#x24 #xE314)
  (#x25 #xE315)
  (#x28 #xE318)
  (#x29 #xE319)
  (#x2E #xE31E)
  (#x2F #xE31F)
  (#x32 #xE322)
  (#x33 #xE323)
  (#x3C #xE32C)
  (#x3D #xE32D)
  (#x40 #xE330)
  (#x41 #xE331)
  (#x44 #xE334)
  (#x45 #xE335)))

;; Diatonic notation
(dia . (
  (#x00 #xE261)
  (#x12 #xE262)
  (#x13 #xE260)
  (#x16 #xE263)
  (#x17 #xE264)
  (#x20 #xE265)
  (#x21 #xE266)
  (#x24 #xF61C)
  (#x25 #xF61D)
  (#x28)
  (#x29)
  (#x2E)
  (#x2F)
  (#x32)
  (#x33)
  (#x3C)
  (#x3D)
  (#x40)
  (#x41)
  (#x44)
  (#x45)))
)


\include "ekmel-main.ily"
