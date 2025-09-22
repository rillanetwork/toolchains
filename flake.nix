{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/25.05";
    flake-utils.url = "github:numtide/flake-utils";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      treefmt-nix,
    }:
    (flake-utils.lib.eachDefaultSystem (
      system:
      let
        # Instantiate package set for the current system.
        pkgs = import nixpkgs { inherit system; };

        # Evaluate the treefmt configuration.
        treefmt = treefmt-nix.lib.evalModule pkgs ./treefmt.nix;
      in
      {
        # `nix fmt`
        formatter = treefmt.config.build.wrapper;

        # `nix flake check`
        checks = {
          formatting = treefmt.config.build.check self;
        };

        # `nix develop`
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = with pkgs; [
            cmake
            ninja
          ];
        };
      }
    ));
}
