{ sources ? import ./nix/sources.nix, pkgs ? import <nixpkgs> {} }:

let

  mutwo-midi = import (sources.mutwo-midi.outPath + "/default.nix");
  mutwo-diary = import "/home/levinericzimmermann/Programming/mutwo.diary/default_local.nix";

  astral = pkgs.python310Packages.buildPythonPackage rec {
    pname = "astral";
    version = "3.2";
  
    src = pkgs.python310Packages.fetchPypi {
      inherit pname version;
      sha256 = "sha256-m3w7QS6eadFyz7JL4Oat3MnxvQGijbi+vmbXXMxTPYg=";
    };
  
    propagatedBuildInputs = with pkgs.python310Packages; [
      pytz
      requests
      freezegun
    ];
  
    checkInputs = with pkgs.python310Packages; [
      pytest
    ];
  
    checkPhase = ''
      py.test -m "not webtest"
    '';
  };

  telemetrix = pkgs.python310Packages.buildPythonPackage rec {
    pname = "telemetrix";
    version = "1.10";

    src = pkgs.python310Packages.fetchPypi {
      inherit pname version;
      sha256 = "sha256-S9hJqk+jLzhf+ZU+I/b1NGb4V+RDC24N3rUxABoVrxo=";
    };

    propagatedBuildInputs = with pkgs.python310Packages; [
      pyserial
    ];

    checkInputs = with pkgs.python310Packages; [
      pytest
    ];
  };

  python94 = pkgs.python310.buildEnv.override {
    extraLibs = with pkgs; [
      astral
      python310Packages.ipython
      python310Packages.ortools
      mutwo-midi
      mutwo-diary
      # controlling diy ebow
      telemetrix
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
