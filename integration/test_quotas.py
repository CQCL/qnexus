"""Test basic functionality relating to the quota module."""

import pandas as pd
import qnexus as qnx
from qnexus.client.models import Quota


def test_quota_getonly(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get a specific Quota."""

    my_quota = qnx.quota.get_only(name="compilation")
    assert isinstance(my_quota, Quota)


def test_quota_get(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get all quotas (currently not a DatabaseIterator)."""

    my_quotas = qnx.quota.get()

    assert len(my_quotas) > 1
    assert isinstance(my_quotas.df(), pd.DataFrame)
    assert isinstance(my_quotas[0], Quota)


def test_check_quota(
    _authenticated_nexus: None,
) -> None:
    """Test that we can check a specific quota guard."""

    # Assumes the user isn't over their Jupyterhub quota
    assert qnx.quota.check_quota(name="jupyterhub") is True
