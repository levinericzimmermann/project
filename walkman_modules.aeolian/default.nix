{ sources ? import ./nix/sources.nix, pkgs ? import <nixpkgs> {} }:

with pkgs.python310Packages;


let

  walkman  = import (sources.walkman.outPath + "/default.nix");

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

in

  buildPythonPackage rec {
    name = "walkman_modules.aeolian";
    src = ./.;
    checkInputs = [
      python310Packages.pytest
    ];
    propagatedBuildInputs = with pkgs.python310Packages; [ 
      walkman
      telemetrix
      numpy
    ];
    checkPhase = ''
      runHook preCheck
      pytest
      runHook postCheck
    '';
    doCheck = false;
  }
