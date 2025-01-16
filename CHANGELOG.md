<!-- This CHANGELOG is populated automatically by commitizen, but can be manually edited if needed. -->

# `qnexus` Release Notes

## 0.10.0 (2025-01-16)


### Added

- Fetch incomplete job results (#131).
- Allow use of scope for single resources (#126).
- Improve typing of decorators (#121).


### Fixed

- Ensure wasm can be extracted from wasm downloaded from nexus (#133).
- Device backend_info pydantic schema generation (#127).


## 0.9.2 (2024-12-18)


### Fixed

- Update quantinuum-schemas to v1.1.0 (#124).


## 0.9.1 (2024-12-05)


### Fixed

- Enum filter serialisation (#120).


## 0.9.0 (2024-11-26)


### Added

- Allow admins to set scope for requests (#118).

### Fixed

- Relaxed dependency version constraints.


## 0.8.1 (2024-11-13)


### Fixed

- Update pytket version to 1.34.

## 0.8.0 (2024-11-12)


### Added

- Pass user_group for job submissions and retries (#92).


### Fixed

- Update websockets dependency to be compatible with pytket-quantinuum (#109).


## 0.7.0 (2024-10-17)


### Added

- Add basic wasm handling (#101).


### Fixed

- Get jobs by id (#106).


## 0.6.1 (2024-10-01)


### Fixed

- Jobs websockets handling.


## 0.6.0 (2024-09-19)


### Added

- Dynamic login and logout (#93).

### Fixed

- Filtering by properties (#95).
- Faster compilation results (#95).
- Summary obtainable for ProjectRef in context (#95).

## 0.5.0 (2024-08-30)


### Added

- Query backend property features (#89).
- Updating and deleting projects (#88).


### Fixed

- Merging properties from context when no properties argument is provided (#91).
- Allow p_meas tuples in h series noise (#85).


## 0.4.1 (2024-08-09)


### Fixed

- Fix retry_status argument in client.

## 0.4.0 (2024-08-09)


### Added

- Added py.typed (#74).


### Fixed

- A bug where job cancellation would result in a 422 error.
- A bug where job retry would result in a serialization error.


## 0.3.0 (2024-08-05)


### Added

- Add qir support (#70).
- Add hypertket support (#71).


## 0.2.0 (2024-07-24)


### Added

- Add function to get h-series circuit cost (#68).


## 0.1.1 (2024-07-19)


### Fixed

- Relax websockets constraint.

## 0.1.0 (2024-07-17)


### Feat

- Save refs to filesystem (#61)
- Project summarize (#60)
- Add utility methods for compiling, executing and creating/getting projects (#45)
- Explicit type signatures for docstrings (#49)
- Use jupyterhub token format and allow configurable token path via env. (#30)
- Add h series noise model (#33)
- Restore some cli functionality (#28)
- Allow querying by properties (#22)
- Allow job properties to be passed (#21)
