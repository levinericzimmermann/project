{ sources ? import ./nix/sources.nix, rsources ? import (sources.mutwo-nix.outPath + "/nix/sources.nix"), pkgs ? import rsources.nixpkgs {}}:
with pkgs.python310Packages;

let

  walkman = import (sources.mutwo-nix.outPath + "/walkman/default.nix") {};

in

  buildPythonPackage rec {
    name = "walkman_modules.mix";
    src = ./.;
    checkInputs = [
      python310Packages.pytest
    ];
    propagatedBuildInputs = with pkgs.python310Packages; [ 
      walkman
    ];
    checkPhase = ''
      runHook preCheck
      pytest
      runHook postCheck
    '';
    doCheck = false;
  }
