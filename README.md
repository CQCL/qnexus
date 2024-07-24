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
- [commitizen](https://commitizen-tools.github.io/commitizen/)

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

### Release

### Step 1 - update the changelog

- Update `CHANGELOG.md`: this is automated. Use `devenv` and the `commitizen` [tool](https://commitizen-tools.github.io/commitizen/):
  ```
  git fetch --tags origin  # make sure your local tags are same as in github
  cz bump --files-only  # --files-only prevents the tool making a git tag
  ```
  This will use the [commit history](https://www.conventionalcommits.org/) and modify `CHANGELOG.md` to include a heading with the new version number and the date. It also updates `.cz.toml`. The tool automatically decides whether to increment the patch version, minor version or major version (major version changes are currently disabled in its config file).
- If you like, you can manually edit `CHANGELOG.md` at this point. Consider moving important entries under these headings, or writing under them (see [Keep A Changelog](https://keepachangelog.com/en/1.1.0/#how)):
  - Deprecated
  - Removed
  - Security
- Create a release branch `git checkout -b release/vx.y.z`
- Update the version in `pyproject.toml` (will be used as the release version).
- `git add` the modifications, then `git commit` and `git push` them.
- Create a PR (title: `docs: Update CHANGELOG for vx.y.z`)
- Ask a colleague to review the changes (should be just `CHANGELOG.md` and `.cz.toml`)
- Squash merge the PR into `main`

### Step 2 - run the release workflow

- On https://github.com/CQCL-DEV/qnexus, via the `make new release` button on the side:
- Select `create new tag` when selecting the tag, with name in the format below.
- Choose the target branch/commit for the release.


## License

This project is licensed under Apache License, Version 2.0 ([LICENSE][] or http://www.apache.org/licenses/LICENSE-2.0).

  [LICENSE]: ./LICENSE


Copyright 2024 Quantinuum Ltd.
