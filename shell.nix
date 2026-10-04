{pkgs ? import <nixpkgs> {}}: let
  inherit (pkgs) lib;
in
  pkgs.mkShell {
    nativeBuildInputs = with pkgs; [uv pyright ruff];

    NIX_LD_LIBRARY_PATH = lib.makeLibraryPath (with pkgs; [
      stdenv.cc.cc.lib
      zlib
      libxcb
      libGL
      glib
    ]);
    NIX_LD = builtins.readFile "${pkgs.stdenv.cc}/nix-support/dynamic-linker";
  }
