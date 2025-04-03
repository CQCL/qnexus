{ pkgs, lib, config, inputs, ... }:
let
  pkgs-unstable = import inputs.nixpkgs-unstable { system = pkgs.stdenv.system; };
in
{

  # https://devenv.sh/packages/
  packages = [ 
    pkgs-unstable.uv
    pkgs.commitizen
    pkgs.git
  ];

  dotenv.enable = true;

  # https://devenv.sh/scripts/
  scripts.qfmt.exec = ''
    echo -e "Running formatting, linting and typechecking 🧹 🔧 \n"

    uv run ruff check --select I --fix
    uv run ruff check 
    uv run ruff format 
    uv run mypy qnexus/ tests/ integration/
  '';

  enterShell = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
    echo -e 'Welcome to the qnexus repo! 😊 ➡️ 🖥️ ➡️ ⚛️\n'
  '';

  # https://devenv.sh/tests/
  enterTest = ''
    echo -e "Running tests \n"
    git --version | grep --color=auto "${pkgs.git.version}"
    uv --version | grep --color=auto "${pkgs-unstable.uv.version}"
    cz version | grep --color=auto "${pkgs.commitizen.version}"
  '';

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
