{ sources ? import ./nix/sources.nix, rsources ? import (sources.mutwo-nix.outPath + "/nix/sources.nix"), pkgs ? import rsources.nixpkgs {}}:
with pkgs.python310Packages;


let

  walkman = import (sources.mutwo-nix.outPath + "/walkman/default.nix") {};

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
  
    nativeCheckInputs = with pkgs.python310Packages; [
      pytest
    ];
  
    checkPhase = ''
      py.test -m "not webtest"
    '';
  };

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
      astral
      time-machine
    ];
    checkPhase = ''
      runHook preCheck
      pytest
      runHook postCheck
    '';
    doCheck = false;
  }
