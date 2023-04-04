{ sources ? import ./nix/sources.nix, rsources ? import (sources.mutwo-nix.outPath + "/nix/sources.nix"), pkgs ? import rsources.nixpkgs {}}:

let

  mutwo-midi = import (sources.mutwo-nix.outPath + "/mutwo.midi/default.nix") {};
  mutwo-diary = import (sources.mutwo-nix.outPath + "/mutwo.diary/default.nix") {};

  walkman-aeolian = import ./walkman_modules.aeolian {};

  yamm = pkgs.python310Packages.buildPythonPackage rec {
    pname = "yamm";
    version = "0.1";
  
    src = pkgs.python310Packages.fetchPypi {
      inherit pname version;
      sha256 = "sha256-bbEUoj27A2PrPRAOYuNbFsdrvisy3Y0DdJCOnhUntQk=";
    };
  
    propagatedBuildInputs = with pkgs.python310Packages; [
    ];
  
    checkInputs = with pkgs.python310Packages; [
      pytest-runner
      pytest
    ];
  
    checkPhase = ''
    '';
  };

  # There is a regression in upstream package,
  python94 = pkgs.python310.buildEnv.override {
    extraLibs = with pkgs; [
      python310Packages.ipython
      python310Packages.ortools
      python310Packages.astropy
      mutwo-midi
      mutwo-diary
      # diy ebow live
      walkman-aeolian
      # markov chain
      yamm
      # moon drawings :)
      python310Packages.pycairo
      # rotate moon drawing
      imagemagick
    ];
  };

in

  pkgs.mkShell {
      buildInputs = with pkgs; [
          jack2
          qjackctl
          python94
          lilypond-with-fonts
          # For generating books
          # texlive.combined.scheme-full
          # Concatenating notes
          # pdftk
          # Needed for various scripts
          arduino-cli
      ];
      shellHook = ''
        umask 0000
        export JACK_PROMISCUOUS_SERVER="jackaudio"
      '';

  }
