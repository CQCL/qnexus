<!-- This CHANGELOG is populated automatically by commitizen, but can be manually edited if needed. -->

# `qnexus` Release Notes

## v0.23.0 (2025-07-22)


### Added

- Add depleted and terminated statuses to JobStatusEnum and related filters.
- Update results fetching to allow incomplete results for different statuses.


## v0.22.0 (2025-07-15)


### Added

- Update to support IBMQ changes: `ibm_instance` and `ibm_region` are now used instead of hub, group, and project.
- Bump dependencies.


## v0.21.0 (2025-07-08)


### Added

- Can now fetch qir results from devices with the newer qsys result format (#208).
- Add qir crud. (#196).


### Fixed

- Cz config and faulty changelog entries.
- Selene integration test now needs new config (#204).
- Update wasm_examples.ipynb to add measures to circuit (#203).


## v0.20.0 (2025-06-05)


### Added

- Accept guppy compiled types in upload (#193).


### Fixed

- Broken job polling when running with nexus_port override (#201).


## v0.19.0 (2025-05-21)


### Added

- Move to the latest jobs api in nexus (#190).


## v0.18.2 (2025-05-15)


### Fixed

- Handle the case when get_passes is called on a compilationresultref without any passes. (#187).
- Change domain (via CONFIG), reload tokens dynamically (#185).


## v0.18.1 (2025-05-13)


### Fixed

- Bump python (#184).
- Don't present unused kwarg for quantinuumconfig (#182).

## v0.18.0 (2025-05-01)


### Added

- Add option to store intermediate compilation results in compile job (#181).
- Enable zstd compression of hugr programs (#179).
- Return an empty dataframe for an empty nexusiterator. (#180).


## v0.17.2 (2025-04-25)


### Fixed

- Update circuit fetching to use migration utility for compatibility (#176).


## v0.17.1 (2025-04-25)


### Fixed

- Update pytket version to 2.3.1 (#175).

## v0.17.0 (2025-04-24)


### Added

- Added delete job method (#172).


### Fixed

- Disable unused and broken jobs and projects cli (#171).


## v0.16.1 (2025-04-10)

### Fixed

- Readd support for python 3.10 (#170).


## v0.16.0 (2025-04-09)


### Added

- Update dependencies (#168).


## v0.15.0 (2025-04-09)


### Added

- Use guppylang qsysresult type (#166).
- Update jobs to v1beta2 api (#163).


### Fixed

- Correct url paths for results (#164).


## v0.14.0 (2025-04-01)


### Changed

- Updated the guppylang version to 0.18.0.


## v0.13.0 (2025-03-31)


### Added

- Experimental workflow for Guppy/HUGR jobs (#152).


## v0.12.0 (2025-03-24)


### Added

- Use newest hugr release and serialise/deserialise using envelope (#150).


### Fixed

- Hugr encoding (#147).


## v0.11.0 (2025-02-28)


### Added

- Get quantinuum device status (#144).
- Headless login (#143).
- Add hugr upload/download (#141).


### Fixed

- Default postprocess to false for execute jobs. (#145).


## v0.10.0 (2025-01-16)


### Added

- Fetch incomplete job results (#131).
- Allow use of scope for single resources (#126).
- Improve typing of decorators (#121).


### Fixed

- Ensure wasm can be extracted from wasm downloaded from nexus (#133).
- Device backend_info pydantic schema generation (#127).


## v0.9.2 (2024-12-18)


### Fixed

- Update quantinuum-schemas to v1.1.0 (#124).


## v0.9.1 (2024-12-05)


### Fixed

- Enum filter serialisation (#120).


## v0.9.0 (2024-11-26)


### Added

- Allow admins to set scope for requests (#118).

### Fixed

- Relaxed dependency version constraints.


## v0.8.1 (2024-11-13)


### Fixed

- Update pytket version to 1.34.

## v0.8.0 (2024-11-12)


### Added

- Pass user_group for job submissions and retries (#92).


### Fixed

- Update websockets dependency to be compatible with pytket-quantinuum (#109).


## v0.7.0 (2024-10-17)


### Added

- Add basic wasm handling (#101).


### Fixed

- Get jobs by id (#106).


## v0.6.1 (2024-10-01)


### Fixed

- Jobs websockets handling.


## v0.6.0 (2024-09-19)


### Added

- Dynamic login and logout (#93).

### Fixed

- Filtering by properties (#95).
- Faster compilation results (#95).
- Summary obtainable for ProjectRef in context (#95).

## v0.5.0 (2024-08-30)


### Added

- Query backend property features (#89).
- Updating and deleting projects (#88).


### Fixed

- Merging properties from context when no properties argument is provided (#91).
- Allow p_meas tuples in h series noise (#85).


## v0.4.1 (2024-08-09)


### Fixed

- Fix retry_status argument in client.

## v0.4.0 (2024-08-09)


### Added

- Added py.typed (#74).


### Fixed

- A bug where job cancellation would result in a 422 error.
- A bug where job retry would result in a serialization error.


## v0.3.0 (2024-08-05)


### Added

- Add qir support (#70).
- Add hypertket support (#71).


## v0.2.0 (2024-07-24)


### Added

- Add function to get h-series circuit cost (#68).


## v0.1.1 (2024-07-19)


### Fixed

- Relax websockets constraint.

## v0.1.0 (2024-07-17)


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
