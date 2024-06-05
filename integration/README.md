# qnexus integration test suite

These tests are intended to be runnable against any Nexus environment by any user (with quotas enabled for basic Nexus usage).
The tests will login the user and create all projects/resources required, deleting them once the test suite has run (TODO).

In general we target the Nexus staging environment at https://staging.myqos.com using the
QA test user with email: 'qa.tket.remote.ext.tests@cambridgequantum.com'.

Requires the following environment variables to be set:

- NEXUS_USER_EMAIL
- NEXUS_USER_PASSWORD
- NEXUS_HOST (to avoid targetting prod by default)
