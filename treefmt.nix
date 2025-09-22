{ ... }:

let
  scripts = "scripts/*";
in
{
  projectRootFile = "flake.nix";

  programs = {
    nixfmt.enable = true;
    shellcheck.enable = true;
    shfmt.enable = true;
    shfmt.indent_size = 4;
    yamlfmt.enable = true;
  };

  settings.formatter = {
    shellcheck.includes = [ scripts ];
    shfmt.includes = [ scripts ];
  };
}
