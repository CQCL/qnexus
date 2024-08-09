<!-- This CHANGELOG is populated automatically by commitizen, but can be manually edited if needed. -->

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

- save refs to filesystem (#61)
- project summarize (#60)
- add utility methods for compiling, executing and creating/getting projects (#45)
- explicit type signatures for docstrings (#49)
- Use jupyterhub token format and allow configurable token path via env. (#30)
- Add h series noise model (#33)
- Restore some cli functionality (#28)
- Allow querying by properties (#22)
- Allow job properties to be passed (#21)

### Fixed

- update small tests (#20)

### Refactor

- use v1beta jobs API and refactor models (#42)
