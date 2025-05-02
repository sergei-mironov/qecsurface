{
  description = "Qecsurface";

  inputs = {
    nixpkgs = {
      url = "github:grwlf/nixpkgs/local17.2";
    };
  };

  outputs = { self, nixpkgs }:
    let
      pkgs = import nixpkgs { system = "x86_64-linux"; };

      texliveFull = pkgs.texlive.combine {
        inherit (pkgs.texlive) scheme-full;
      };

    in {
      packages = {
        x86_64-linux = self.defaultPackage.x86_64-linux;
      };
      defaultPackage = {
        x86_64-linux = self.devEnvironment;
      };
      devShells = {
        x86_64-linux = self.devEnvironment;
      };
      devEnvironment = pkgs.mkShell {
        buildInputs = ([
          (pkgs.python3.withPackages (p: with p; [ ipython scipy ortools python-lsp-server]))
          texliveFull
        ]) ++
        (with pkgs ; [
          xdotool
          yq
        ]);

        shellHook = ''
          . ./env.sh
          echo "Sourced ./env.sh"
        '';
      };
    };
}

