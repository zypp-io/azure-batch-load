import pytest
from azure.identity import DefaultAzureCredential

from azurebatchload.checks import Checks
from azurebatchload.core import Base
from azurebatchload.download import Download
from azurebatchload.utils import Utils

ACCOUNT_KEY = "a2V5"
CONNECTION_STRING = (
    f"DefaultEndpointsProtocol=https;AccountName=acct;AccountKey={ACCOUNT_KEY};EndpointSuffix=core.windows.net"
)


@pytest.fixture(autouse=True)
def clear_storage_env(monkeypatch):
    for var in ("AZURE_STORAGE_CONNECTION_STRING", "AZURE_STORAGE_ACCOUNT", "AZURE_STORAGE_KEY"):
        monkeypatch.delenv(var, raising=False)


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
