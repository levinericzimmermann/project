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
%% File: ekmel-arabic.ily  -  Include file for Arabic scores (24-EDO)
%% Latest revision: 28 February 2022
%%
%% This file is a variant of "ekmel-24.ily" for Arabic scores, like
%% LilyPond's "arabic.ly" but with the correct accidentals
%% (U+ED30 - U+ED38 in SMuFL).
%% It supports Arabic maqamat and defines only the Arabic notation and
%% Italian note names, so the commands \ekmelicStyle and \language are
%% not required.
%%
%% The tables of Arabic maqamat are taken from "arabic.ly"
%% Copyright (C) 2017 Amir Czwink <amir130@hotmail.de>
%% Copyright (C) 2008 Neil Puttock
%%

\version "2.19.22"


% Tuning table
ekmTuning = #'(
  (#x1A . 1/4)
  (#x28 . 1/2)
  (#x36 . 3/4)
  (#x44 . 1)
  (#x50 . 5/4))


% Language tables
ekmLanguages = #'(
(italiano . (
  (dobb 0 . #x45)
  (dobsb 0 . #x37)
  (dob 0 . #x29)
  (dosb 0 . #x1B)
  (do 0 . 0)
  (dosd 0 . #x1A)
  (dod 0 . #x28)
  (dodsd 0 . #x36)
  (dodd 0 . #x44)
  (rebb 1 . #x45)
  (rebsb 1 . #x37)
  (reb 1 . #x29)
  (resb 1 . #x1B)
  (re 1 . 0)
  (resd 1 . #x1A)
  (red 1 . #x28)
  (redsd 1 . #x36)
  (redd 1 . #x44)
  (mibb 2 . #x45)
  (mibsb 2 . #x37)
  (mib 2 . #x29)
  (misb 2 . #x1B)
  (mi 2 . 0)
  (misd 2 . #x1A)
  (mid 2 . #x28)
  (midsd 2 . #x36)
  (midd 2 . #x44)
  (fabb 3 . #x45)
  (fabsb 3 . #x37)
  (fab 3 . #x29)
  (fasb 3 . #x1B)
  (fa 3 . 0)
  (fasd 3 . #x1A)
  (fad 3 . #x28)
  (fadsd 3 . #x36)
  (fadd 3 . #x44)
  (solbb 4 . #x45)
  (solbsb 4 . #x37)
  (solb 4 . #x29)
  (solsb 4 . #x1B)
  (sol 4 . 0)
  (solsd 4 . #x1A)
  (sold 4 . #x28)
  (soldsd 4 . #x36)
  (soldd 4 . #x44)
  (labb 5 . #x45)
  (labsb 5 . #x37)
  (lab 5 . #x29)
  (lasb 5 . #x1B)
  (la 5 . 0)
  (lasd 5 . #x1A)
  (lad 5 . #x28)
  (ladsd 5 . #x36)
  (ladd 5 . #x44)
  (sibb 6 . #x45)
  (sibsb 6 . #x37)
  (sib 6 . #x29)
  (sisb 6 . #x1B)
  (si 6 . 0)
  (sisd 6 . #x1A)
  (sid 6 . #x28)
  (sidsd 6 . #x36)
  (sidd 6 . #x44)))
)


% Notation tables
ekmNotations = #'(
(arabic . (
  (#x00 #xED34)
  (#x1A #xED35)
  (#x1B #xED33)
  (#x28 #xED36)
  (#x29 #xED32)
  (#x36 #xED37)
  (#x37 #xED31)
  (#x44 #xED38)
  (#x45 #xED30)
  (#x50 #xED35 #xED38)
  (#x51 #xED33 #xED30)
  (#x21A #xED33 #xED36)
  (#x21B #xED35 #xED32)
  (#x236 #xED33 #xED38)
  (#x237 #xED35 #xED30)))
)


\include "ekmel-main.ily"


%
% Arabic maqamat ordered by maqam family
%

% Bayati family
bayati = #`(
  (0 . ,NATURAL)
  (1 . ,SEMI-FLAT)
  (2 . ,FLAT)
  (3 . ,NATURAL)
  (4 . ,NATURAL)
  (5 . ,FLAT)
  (6 . ,FLAT)
)

% Hijaz family
hijaz = #`(
  (0 . ,NATURAL)
  (1 . ,FLAT)
  (2 . ,NATURAL)
  (3 . ,NATURAL)
  (4 . ,NATURAL)
  (5 . ,FLAT)
  (6 . ,FLAT)
)

hijaz_kar = #`(
  (0 . ,NATURAL)
  (1 . ,FLAT)
  (2 . ,NATURAL)
  (3 . ,NATURAL)
  (4 . ,NATURAL)
  (5 . ,FLAT)
  (6 . ,NATURAL)
)

% Kurd/Kurdi family
kurd = #`(
  (0 . ,NATURAL)
  (1 . ,FLAT)
  (2 . ,FLAT)
  (3 . ,NATURAL)
  (4 . ,NATURAL)
  (5 . ,FLAT)
  (6 . ,FLAT)
)

% Rast family
rast = #`(
  (0 . ,NATURAL)
  (1 . ,NATURAL)
  (2 . ,SEMI-FLAT)
  (3 . ,NATURAL)
  (4 . ,NATURAL)
  (5 . ,NATURAL)
  (6 . ,SEMI-FLAT)
)

% Sikah family
sikah = #`(
  (0 . ,NATURAL)
  (1 . ,SEMI-FLAT)
  (2 . ,SEMI-FLAT)
  (3 . ,SEMI-SHARP)
  (4 . ,NATURAL)
  (5 . ,SEMI-FLAT)
  (6 . ,SEMI-FLAT)
)

iraq = #`(
  (0 . ,NATURAL)
  (1 . ,SEMI-FLAT)
  (2 . ,SEMI-FLAT)
  (3 . ,NATURAL)
  (4 . ,SEMI-FLAT)
  (5 . ,SEMI-FLAT)
  (6 . ,SEMI-FLAT)
)


% Alteration order for key signatures with quarter tones
\layout {
  \context {
    \Score
    keyAlterationOrder = #'(
      (6 . -1/2) (2 . -1/2) (5 . -1/2) (1 . -1/2) (4 . -1/2) (0 . -1/2) (3 . -1/2)
      (6 . -1/4) (2 . -1/4) (5 . -1/4) (1 . -1/4) (4 . -1/4) (0 . -1/4) (3 . -1/4)
      (3 .  1/2) (0 .  1/2) (4 .  1/2) (1 .  1/2) (5 .  1/2) (2 .  1/2) (6 .  1/2)
      (3 .  1/4) (0 .  1/4) (4 .  1/4) (1 .  1/4) (5 .  1/4) (2 .  1/4) (6 .  1/4)
      (6 .   -1) (2 .   -1) (5 .   -1) (1 .   -1) (4 .   -1) (0 .   -1) (3 .   -1)
      (3 .    1) (0 .    1) (4 .    1) (1 .    1) (5 .    1) (2 .    1) (6 .    1)
    )
  }
}
