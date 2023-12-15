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
            python310Packages.requests
            python310Packages.matplotlib
            python310Packages.kafka-python
            kubectl
            minikube
            kubernetes-helm
          ];
          shellHook = ''
            alias dc="docker compose"
            alias spark="docker exec -it prime_spark /opt/bitnami/spark/bin/spark-submit /opt/bitnami/spark/work/"
            alias kafkaLogs="docker exec -it prime_kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic"
          '';
        };

      });
}
