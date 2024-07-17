{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "qnexus-dev-shell";

  buildInputs = with pkgs; [ 
    poetry
    commitizen
  ];

  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
}
