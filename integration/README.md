# qnexus integration test suite

These tests are intended to be runnable against any Nexus environment by any user (with quotas enabled for basic Nexus usage).
The tests will login the user and create all projects/resources required, deleting them once the test suite has run.

In general we target the Nexus QA environment at https://qa.myqos.com using the
QA test user with email: 'qa_nexus_staging_pytket-nexus@mailsac.com'.

Requires the following environment variables to be set:

- NEXUS_QA_USER_EMAIL
- NEXUS_QA_USER_PASSWORD
- NEXUS_DOMAIN (to avoid targetting prod by default)
- NEXUS_QA_QSYS_DEVICE (for executing HUGR programs on a next-gen qsys device)


You can then set up the auth tokens for the NEXUS_USER_EMAIL user with:

```sh
uv run python integration/setup_tokens.py
```

And run the tests with:

```sh
uv run pytest integration/
```