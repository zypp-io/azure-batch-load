import subprocess
from datetime import datetime, timedelta, timezone

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas

from azurebatchload.checks import Checks

# Azure caps user delegation keys at 7 days from the current (server) time.
# Stay a few minutes inside that window to tolerate clock skew.
MAX_USER_DELEGATION_DAYS = 7
CLOCK_SKEW_MARGIN = timedelta(minutes=5)


class Base(Checks):
    def __init__(
        self,
        destination,
        folder,
        extension=None,
        modified_since=None,
        method="batch",
        list_files=None,
        expiry_download_links=7,
    ):
        super().__init__(directory=folder)

        self.destination = destination
        self.folder = folder
        self.extension = extension
        self.modified_since = modified_since
        if not self._check_azure_cli_installed():
            self.method = "single"
        else:
            self.method = method
        self.list_files = list_files
        credentials = self._check_connection_credentials()
        self.connection_string = credentials[0]
        self.account_name = credentials[1]
        self.account_key = credentials[2]
        self.expiry_download_links = expiry_download_links
        self._blob_service_client = None
        self._user_delegation_key = None

    def checks(self):
        allowed_methods = ("batch", "single")
        if self.method not in allowed_methods:
            raise ValueError(f"Method {self.method} is not a valid method. Choose from {' or '.join(allowed_methods)}.")

        if self.list_files and self.method == "batch":
            raise ValueError("list_files is only allowed with method='single'.")

        if self.list_files and not isinstance(self.list_files, list):
            raise ValueError(f"Argument list_files was set, but is not of type list, but type {type(self.list_files)}")

    def _get_blob_service_client(self) -> BlobServiceClient:
        # one client (and credential) per run, so the token is fetched once
        if self._blob_service_client is None:
            if self.connection_string:
                self._blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            else:
                # passwordless: az login locally, managed identity on Azure
                self._blob_service_client = BlobServiceClient(
                    account_url=f"https://{self.account_name}.blob.core.windows.net",
                    credential=DefaultAzureCredential(),
                )

        return self._blob_service_client

    def _cli_auth_flags(self) -> dict:
        if self.connection_string:
            return {"--connection-string": self.connection_string}

        # passwordless: az uses its own session (az login / az login --identity)
        return {"--account-name": self.account_name, "--auth-mode": "login"}

    @staticmethod
    def _run_cli(command, flags):
        """
        Run an Azure CLI command and raise when it fails, instead of continuing as if it worked.

        Parameters
        ----------
        command: the az command with its positional arguments
        flags: optional flags, flags with an empty value are left out
        """
        cmd = command
        for flag, value in flags.items():
            if value:
                cmd = f"{cmd} {flag} '{value}'"

        exit_code = subprocess.run(cmd, shell=True).returncode
        if exit_code != 0:
            # cmd can hold a connection string, so only name the az command itself
            name = command.split(" -")[0]
            raise RuntimeError(f"{name} failed with exit code {exit_code}, see the Azure CLI output above.")

    def _check_link_expiry(self):
        if self.expiry_download_links <= 0:
            raise ValueError(
                f"expiry_download_links has to be a positive number of days, got {self.expiry_download_links}."
            )

        if not self.account_key and self.expiry_download_links > MAX_USER_DELEGATION_DAYS:
            raise ValueError(
                f"expiry_download_links can be at most {MAX_USER_DELEGATION_DAYS} days "
                f"without an account key, got {self.expiry_download_links}."
            )

    def _get_user_delegation_key(self):
        """
        Fetch one user delegation key per run and reuse it for every download link.

        Returns
        -------
        user delegation key, expiry of the key (and of the links signed with it)
        """
        if self._user_delegation_key is None:
            now = datetime.now(timezone.utc)
            start = now - CLOCK_SKEW_MARGIN
            expiry = min(
                now + timedelta(days=self.expiry_download_links),
                start + timedelta(days=MAX_USER_DELEGATION_DAYS),
            )
            key = self._get_blob_service_client().get_user_delegation_key(key_start_time=start, key_expiry_time=expiry)
            self._user_delegation_key = key, expiry

        return self._user_delegation_key

    def create_blob_link(self, blob_folder, blob_name) -> str:
        self._check_link_expiry()

        if blob_folder:
            full_path_blob = f"{blob_folder}/{blob_name}"
        else:
            full_path_blob = blob_name
        url = f"https://{self.account_name}.blob.core.windows.net/{self.destination}/{full_path_blob}"

        if self.account_key:
            signing_key = {"account_key": self.account_key}
            expiry = datetime.now(timezone.utc) + timedelta(days=self.expiry_download_links)
        else:
            # passwordless: sign with a user delegation key (Entra identity) instead of the account key
            user_delegation_key, expiry = self._get_user_delegation_key()
            signing_key = {"user_delegation_key": user_delegation_key}

        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.destination,
            blob_name=full_path_blob,
            permission=BlobSasPermissions(read=True, delete_previous_version=False),
            expiry=expiry,
            **signing_key,
        )

        url_with_sas = f"{url}?{sas_token}"
        return url_with_sas

    @staticmethod
    def create_not_case_sensitive_extension(extension):
        """
        We create in-case sensitive fnmatch
        .pdf -> .[Pp][Dd][Ff]
        .csv -> .[Cc][Ss][Vv]
        """
        new_extension = ""
        for letter in extension:
            if not letter.isalpha():
                new_extension += letter
            else:
                new_extension += f"[{letter.upper()}{letter}]"

        if not new_extension.startswith("*"):
            new_extension = "*" + new_extension

        return new_extension

    def define_pattern(self):
        self.extension = self.create_not_case_sensitive_extension(self.extension)
        if self.folder and not self.extension:
            if self.folder.endswith("/"):
                pattern = self.folder + "*"
            else:
                pattern = self.folder + "/*"
        elif self.folder and self.extension:
            pattern = self.folder.rstrip("/") + "/" + "*" + self.extension
        elif not self.folder and self.extension:
            pattern = "*" + self.extension
        else:
            pattern = None

        return pattern
