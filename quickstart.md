# qnexus

[Quantinuum Nexus](https://nexus.quantinuum.com) python client.


```python
import qnexus as qnx

# Will open a browser window to login with Nexus credentials
qnx.login()

# Dataframe representation of all your pending jobs in Nexus
qnx.jobs.get_all(job_status=["SUBMITTED", "QUEUED", "RUNNING"]).df()
```

Full documentation available at https://docs.quantinuum.com/nexus

Copyright 2025 Quantinuum Ltd.
