# qnexus integration test suite

Requires the following environment variables:

- NEXUS_USER_EMAIL
- NEXUS_USER_PASSWORD


To avoid running tests that have side effects (such as the creation or deletion of data), use:

```
poetry run pytest -m "not create"
