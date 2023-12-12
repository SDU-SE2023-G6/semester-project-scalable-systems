{

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    utils.url = "github:numtide/flake-utils";
    utils.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, ... }@inputs:
    inputs.utils.lib.eachSystem [ "x86_64-linux" ] (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ ];
          config.allowUnfree = true;
        };
      in {
        devShell = pkgs.mkShell rec {

          packages = with pkgs; [
            python310
            python310Packages.pip
            python310Packages.pyspark
            python310Packages.pandas
            python310Packages.numpy
          ];
          shellHook = ''
            alias spark="docker run -it --rm -p 4040:4040 -v $(pwd)/sparkvol:/opt/spark/work-dir/sparkvol --network host spark:python3 /opt/spark/bin/pyspark"
          '';
        };

      });
}
