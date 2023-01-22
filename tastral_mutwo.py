#! /usr/bin/env nix-shell
#! nix-shell -i python --pure ../shell.nix

from mutwo import project_parameters

print(project_parameters.MoonPhase.NEW)
print(project_parameters.MoonPhase.NEW.value)
