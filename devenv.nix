{ pkgs, lib, config, inputs, ... }:

{

  # https://devenv.sh/packages/
  packages = [ 
    pkgs.poetry
    pkgs.commitizen
  ];

  # https://devenv.sh/scripts/
  scripts.fmt.exec = ''
    # Script to run formatting, liniting and type checking tools

    poetry run isort qnexus/ tests/ integration/
    poetry run black qnexus/ tests/ integration/
    poetry run pylint qnexus/ tests/ integration/
    poetry run mypy qnexus/ tests/ integration/ --namespace-packages
  '';

  enterShell = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
    echo 'Welcome to the qnexus repo'
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
