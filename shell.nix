{ sources ? import ./nix/sources.nix, rsources ? import (sources.mutwo-nix.outPath + "/nix/sources.nix"), pkgs ? import rsources.nixpkgs {}}:

with pkgs;
with pkgs.python310Packages;

let

  mutwo-diary   = import (sources.mutwo-nix.outPath + "/mutwo.diary/default.nix") {};
  mutwo-music   = import (sources.mutwo-nix.outPath + "/mutwo.music/default.nix") {};
  mutwo-midi    = import (sources.mutwo-nix.outPath + "/mutwo.midi/default.nix") {};

  mutwo-kepathian = import ./mutwo.kepathian/default.nix {};
  mutwo-mmml = import ./mutwo.mmml/default.nix {};

  mypython = python310.buildEnv.override {
    extraLibs = [
      ipython
      mutwo-midi
      mutwo-kepathian
      mutwo-mmml
      mutwo-diary

      # Strange bug: mido needs it, but for some reason mutwo.midi
      # doesn't deliver it.
      packaging
    ];
  };

in

  pkgs.mkShell {
      buildInputs = with pkgs; [
          mypython

          # To render documents
          # (should actually be included in mutwo-kepathian, Idk why
          # it isn't)
          sile
      ];
  }
