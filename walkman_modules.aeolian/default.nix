{ sources ? import ./nix/sources.nix, pkgs ? import <nixpkgs> {} }:

with pkgs.python310Packages;


let

  walkman  = import (sources.walkman.outPath + "/default.nix");

in

  buildPythonPackage rec {
    name = "walkman_modules.aeolian";
    src = ./.;
    checkInputs = [
      python310Packages.pytest
    ];
    propagatedBuildInputs = with pkgs.python310Packages; [ 
      walkman
      pyserial
      numpy
    ];
    checkPhase = ''
      runHook preCheck
      pytest
      runHook postCheck
    '';
    doCheck = false;
  }
