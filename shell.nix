{ sources ? import ./nix/sources.nix, pkgs ? import <nixpkgs> {} }:

let

  mutwo-midi = import (sources.mutwo-midi.outPath + "/default.nix");
  mutwo-diary = import "/home/levinericzimmermann/Programming/mutwo.diary/default_local.nix";

  walkman-aeolian = import ./walkman_modules.aeolian { };

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

  python94 = pkgs.python310.buildEnv.override {
    extraLibs = with pkgs; [
      astral
      python310Packages.ipython
      python310Packages.ortools
      mutwo-midi
      mutwo-diary
      # diy ebow live
      walkman-aeolian
      # markov chain
      yamm
    ];
  };

in

  pkgs.mkShell {
      buildInputs = with pkgs; [
          python94
          lilypond-with-fonts
          # For generating books
          texlive.combined.scheme-full
      ];
  }
