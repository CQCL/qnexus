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
  scripts.fmt.exec = ''
    # Script to run formatting, liniting and type checking tools

    uv run isort qnexus/ tests/ integration/
    uv run black qnexus/ tests/ integration/
    uv run pylint qnexus/ tests/ integration/
    uv run mypy qnexus/ tests/ integration/ --namespace-packages
  '';

  enterShell = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
    echo -e 'Welcome to the qnexus repo! 😊 ➡️ 🖥️ ➡️ ⚛️\n'
  '';

  # https://devenv.sh/tasks/
  # tasks = {
  #   "myproj:setup".exec = "mytool build";
  #   "devenv:enterShell".after = [ "myproj:setup" ];
  # };

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
