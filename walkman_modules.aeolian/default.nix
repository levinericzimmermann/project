{ sources ? import ./nix/sources.nix, pkgs ? import <nixpkgs> {} }:

with pkgs.python310Packages;


let

  walkman  = import (sources.walkman.outPath + "/default.nix");

  walkmanio = pkgs.python310Packages.buildPythonPackage rec {
    pname = "walkmanio";
    version = "0.1.0";
    src = ./walkmanio;
    propagatedBuildInputs = with pkgs.python310Packages; [
    ];
    checkInputs = with pkgs.python310Packages; [
    ];
    checkPhase = ''
    '';
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
      walkmanio
      pyserial
      numpy
      APScheduler
    ];
    checkPhase = ''
      runHook preCheck
      pytest
      runHook postCheck
    '';
    doCheck = false;
  }
