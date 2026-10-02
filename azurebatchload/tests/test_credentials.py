from datetime import datetime, timedelta, timezone

import pytest
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient, UserDelegationKey

from azurebatchload.checks import Checks
from azurebatchload.core import Base
from azurebatchload.download import Download
from azurebatchload.upload import Upload
from azurebatchload.utils import Utils

ACCOUNT_KEY = "a2V5"
CONNECTION_STRING = (
    f"DefaultEndpointsProtocol=https;AccountName=acct;AccountKey={ACCOUNT_KEY};EndpointSuffix=core.windows.net"
)


@pytest.fixture(autouse=True)
def clear_storage_env(monkeypatch):
    for var in ("AZURE_STORAGE_CONNECTION_STRING", "AZURE_STORAGE_ACCOUNT", "AZURE_STORAGE_KEY"):
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def delegation_key_requests(monkeypatch):
    """Stub the Get User Delegation Key call (network) and record each requested (start, expiry)."""
    requests = []

    def get_user_delegation_key(self, key_start_time, key_expiry_time, **kwargs):
        requests.append((key_start_time, key_expiry_time))
        key = UserDelegationKey()
        key.signed_oid = "oid"
        key.signed_tid = "tid"
        key.signed_start = key_start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        key.signed_expiry = key_expiry_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        key.signed_service = "b"
        key.signed_version = "2021-08-06"
        key.value = ACCOUNT_KEY
        return key

    monkeypatch.setattr(BlobServiceClient, "get_user_delegation_key", get_user_delegation_key)
    return requests


def test_account_name_only_is_passwordless(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")

    assert Checks(directory=None)._check_connection_credentials() == (None, "acct", None)


def test_no_credentials_raises():
    with pytest.raises(ValueError, match="AZURE_STORAGE_ACCOUNT"):
        Checks(directory=None)._check_connection_credentials()


def test_connection_string_still_supported(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", CONNECTION_STRING)

    assert Checks(directory=None)._check_connection_credentials() == (CONNECTION_STRING, "acct", ACCOUNT_KEY)


def test_blob_service_client_uses_default_azure_credential(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")

    client = Base(destination="container", folder=None)._get_blob_service_client()

    assert isinstance(client.credential, DefaultAzureCredential)
    assert client.url == "https://acct.blob.core.windows.net/"


def test_blob_service_client_uses_connection_string(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", CONNECTION_STRING)

    client = Base(destination="container", folder=None)._get_blob_service_client()

    assert client.credential.account_name == "acct"
    assert client.credential.account_key == ACCOUNT_KEY


def test_blob_service_client_reused_within_a_run(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")
    base = Base(destination="container", folder=None)

    assert base._get_blob_service_client() is base._get_blob_service_client()


def test_utils_works_without_connection_string(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")

    utils = Utils(container="container")

    assert isinstance(utils._container_client.credential, DefaultAzureCredential)


def test_cli_auth_flags_passwordless(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")

    flags = Base(destination="container", folder=None)._cli_auth_flags()

    assert flags == {"--account-name": "acct", "--auth-mode": "login"}


def test_cli_auth_flags_connection_string(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", CONNECTION_STRING)

    flags = Base(destination="container", folder=None)._cli_auth_flags()

    assert flags == {"--connection-string": CONNECTION_STRING}


def test_download_batch_command_is_passwordless(monkeypatch, tmp_path):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")
    commands = []
    monkeypatch.setattr("azurebatchload.download.os.system", commands.append)

    Download(destination=str(tmp_path), source="container", extension=".pdf")._download_batch()

    assert "--account-name 'acct' --auth-mode 'login'" in commands[0]
    assert "--connection-string" not in commands[0]


def test_blob_link_is_user_delegation_sas_when_passwordless(monkeypatch, delegation_key_requests):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")

    link = Base(destination="container", folder=None).create_blob_link("folder", "a.pdf")

    assert link.startswith("https://acct.blob.core.windows.net/container/folder/a.pdf?")
    assert "skoid=oid" in link
    assert "sp=r" in link


def test_user_delegation_key_requested_once_per_run(monkeypatch, delegation_key_requests):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")
    base = Base(destination="container", folder=None)

    base.create_blob_link("folder", "a.pdf")
    base.create_blob_link("folder", "b.pdf")

    assert len(delegation_key_requests) == 1


def test_user_delegation_key_valid_at_most_seven_days(monkeypatch, delegation_key_requests):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")

    Base(destination="container", folder=None, expiry_download_links=7).create_blob_link(None, "a.pdf")

    start, expiry = delegation_key_requests[0]
    assert expiry - start <= timedelta(days=7)


def test_user_delegation_key_expiry_leaves_clock_skew_margin(monkeypatch, delegation_key_requests):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")

    Base(destination="container", folder=None, expiry_download_links=7).create_blob_link(None, "a.pdf")

    _, expiry = delegation_key_requests[0]
    assert expiry <= datetime.now(timezone.utc) + timedelta(days=7) - timedelta(minutes=5)


def test_long_expiry_allowed_when_no_links_are_created(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")

    Base(destination="container", folder=None, expiry_download_links=30)


def test_link_with_expiry_over_seven_days_rejected_when_passwordless(monkeypatch, delegation_key_requests):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")
    base = Base(destination="container", folder=None, expiry_download_links=8)

    with pytest.raises(ValueError, match="7 days"):
        base.create_blob_link(None, "a.pdf")
    assert delegation_key_requests == []


def test_upload_with_links_rejects_long_expiry_before_uploading(monkeypatch, tmp_path):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")
    (tmp_path / "a.pdf").write_bytes(b"a")
    uploads = []
    monkeypatch.setattr(ContainerClient, "upload_blob", lambda self, *args, **kwargs: uploads.append(kwargs))
    upload = Upload(
        destination="container",
        source=str(tmp_path),
        method="single",
        create_download_links=True,
        expiry_download_links=8,
    )

    with pytest.raises(ValueError, match="7 days"):
        upload.upload()
    assert uploads == []


def test_negative_expiry_rejected_when_passwordless(monkeypatch, delegation_key_requests):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "acct")
    base = Base(destination="container", folder=None, expiry_download_links=-1)

    with pytest.raises(ValueError, match="positive"):
        base.create_blob_link(None, "a.pdf")
    assert delegation_key_requests == []


def test_zero_expiry_rejected_with_account_key(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", CONNECTION_STRING)
    base = Base(destination="container", folder=None, expiry_download_links=0)

    with pytest.raises(ValueError, match="positive"):
        base.create_blob_link(None, "a.pdf")


def test_blob_link_signed_with_account_key_when_available(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", CONNECTION_STRING)

    link = Base(destination="container", folder=None, expiry_download_links=30).create_blob_link(None, "a.pdf")

    assert "sig=" in link
    assert "skoid=" not in link
