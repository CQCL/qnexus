"""Client API for devices in Nexus."""

from qnexus.client import nexus_client
from qnexus.exceptions import ResourceFetchFailed
from qnexus.models import (
    Credential,
    Device,
    IssuerEnum,
    StoredBackendInfo,
    issuer_enum_to_config_str,
)
from qnexus.models.filters import DevicesFilter
from qnexus.models.references import DataframableList


class Params(DevicesFilter):
    """Params for filtering devices."""


def get_all(
    issuers: list[IssuerEnum] | None = None,
    aws_region: str | None = None,
    ibmq_hub: str | None = None,
    ibmq_group: str | None = None,
    ibmq_project: str | None = None,
    credentials: list[Credential] | None = None,
    credential_names: list[str] | None = None,
    nexus_hosted: bool | None = None,
) -> DataframableList[Device]:
    """Get all available devices."""

    issuer_config_names = (
        [
            config_str
            for issuer in issuers
            for config_str in issuer_enum_to_config_str(issuer)
        ]
        if issuers
        else []
    )

    params = Params(
        backend=issuer_config_names if issuer_config_names else None,
        region=aws_region,
        ibmq_hub=ibmq_hub,
        ibmq_group=ibmq_group,
        ibmq_project=ibmq_project,
        credential_ids=[cred.id for cred in credentials] if credentials else None,
        credential_names=credential_names,
        is_local=nexus_hosted,
    ).model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)

    res = nexus_client.get(
        "/api/v5/available_devices",
        params=params,
    )

    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    device_list: DataframableList[Device] = DataframableList([])

    for backendinfolist in res.json():
        for backend_info in backendinfolist["backend_info_list"]:
            # Clean up the backend name for user consumption
            backend_name = backend_info["name"].replace("Backend", "")
            backend_name = backend_name.replace("EmulatorEnabled", "")

            device_list.append(
                Device(
                    backend_name=backend_name,
                    device_name=backend_info["device_name"],
                    nexus_hosted=backendinfolist["is_local"],
                    backend_info=StoredBackendInfo(
                        **backend_info
                    ).to_pytket_backend_info(),
                )
            )

    return device_list
