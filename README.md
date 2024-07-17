# qnexus



[![pypi][]](https://pypi.org/project/qnexus/)
[![py-version][]](https://pypi.org/project/qnexus/)

  [py-version]: https://img.shields.io/pypi/pyversions/qnexus
  [pypi]: https://img.shields.io/pypi/v/qnexus

A python client for the [Quantinuum Nexus](https://nexus.quantinuum.com) platform.

```python
import qnexus as qnx

# Will open a browser window to login with Nexus credentials
qnx.login()

# Dataframe representation of all your pending jobs in Nexus
qnx.jobs.get_all(job_status=["SUBMITTED", "QUEUED", "RUNNING"]).df()
```


## Install

qnexus can be installed via `pip`.

```sh
pip install qnexus
```


## Usage

Usage examples and tutorials are available [here][examples].

[examples]: ./examples/


## Development

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python >= 3.10
- [Poetry](https://python-poetry.org/docs/#installation)

If you have [Nix](https://zero-to-nix.com/start/install) and [direnv](https://github.com/direnv available on your system you can reuse the nix shell environment to provide a development environment.

### Installing

Run the following to setup your virtual environment and install dependencies:

```sh
poetry install
```

You can then activate the virtual environment and work within it with:

```sh
poetry shell
```

To run a single command in the shell, just prefix it with `poetry run`.


### Checks

Formatting, linting and type-checking can be done with:

```sh
poetry run scripts/fmt.sh
```

### Testing

Most of the test suite are integration tests that require the following environment variables:

NEXUS_HOST = "staging.myqos.com"
NEXUS_QA_USER_EMAIL = ...
NEXUS_QA_USER_PASSWORD = ...

And can be run with:

```sh
poetry run pytest integration/
```

Run basic unit tests using

```sh
poetry run pytest tests/
```

## License

This project is licensed under Apache License, Version 2.0 ([LICENCE][] or http://www.apache.org/licenses/LICENSE-2.0).

  [LICENCE]: ./LICENCE