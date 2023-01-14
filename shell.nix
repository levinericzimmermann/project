{ sources ? import ./nix/sources.nix, pkgs ? import <nixpkgs> {} }:

let

  mutwo-midi = import (sources.mutwo-midi.outPath + "/default.nix");
  mutwo-diary = import "/home/levinericzimmermann/Programming/mutwo.diary/default_local.nix";

  python94 = pkgs.python310.buildEnv.override {
    extraLibs = with pkgs; [
      python310Packages.ipython
      python310Packages.ortools
      mutwo-midi
      mutwo-diary
    ];
  };

in

  pkgs.mkShell {
      buildInputs = with pkgs; [
          python94
          lilypond-with-fonts
      ];
  }
