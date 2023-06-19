{ sources ? import ./nix/sources.nix, rsources ? import (sources.mutwo-nix.outPath + "/nix/sources.nix"), pkgs ? import rsources.nixpkgs {}}:

let

  mutwo-midi = import (sources.mutwo-nix.outPath + "/mutwo.midi/default.nix") {};
  mutwo-diary = import (sources.mutwo-nix.outPath + "/mutwo.diary/default.nix") {};

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

  # walkman = import (sources.mutwo-nix.outPath + "/walkman/default.nix") {};
  walkman-mix = import ./mix.nix {};

  python94 = pkgs.python310.buildEnv.override {
    extraLibs = with pkgs.python310Packages; [
      ipython
      ortools
      mutwo-midi
      mutwo-diary
      # markov chain
      yamm
      # live electronics
      walkman-mix
    ];
  };

in

  pkgs.mkShell {
      buildInputs = with pkgs; [
          python94
          lilypond-with-fonts
          ecasound # for simulation
      ];
  }
