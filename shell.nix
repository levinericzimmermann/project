{ sources ? import ./nix/sources.nix, rsources ? import (sources.mutwo-nix.outPath + "/nix/sources.nix"), pkgs ? import rsources.nixpkgs {}}:

let

  mutwo-common  = import (sources.mutwo-nix.outPath + "/mutwo.common/default.nix") {};
  mutwo-midi    = import (sources.mutwo-nix.outPath + "/mutwo.midi/default.nix") {};
  mutwo-diary   = import (sources.mutwo-nix.outPath + "/mutwo.diary/default.nix") {};

  mypython = pkgs.python310.buildEnv.override {
    extraLibs = with pkgs.python310Packages; [
      ipython
      mutwo-midi
      mutwo-common
      mutwo-diary
    ];
  };

in

  pkgs.mkShell {
      buildInputs = with pkgs; [
          mypython
          lilypond-with-fonts
      ];
  }
