{ sources ? import ./nix/sources.nix, rsources ? import (sources.mutwo-nix.outPath + "/nix/sources.nix"), pkgs ? import rsources.nixpkgs {}}:

let

  mutwo-midi = import (sources.mutwo-nix.outPath + "/mutwo.midi/default.nix") {};
  mutwo-diary = import (sources.mutwo-nix.outPath + "/mutwo.diary/default.nix") {};

  python94 = pkgs.python310.buildEnv.override {
    extraLibs = with pkgs.python310Packages; [
      ipython
      ortools
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
