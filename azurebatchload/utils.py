import os
import subprocess
from azure.storage.blob import BlobServiceClient
from azurebatchload.checks import Checks


class Utils(Checks):
    def __init__(
        self, container, connection_string=None, account_key=None, account_name=None, verbose=None
    ):
        super().__init__(connection_string, account_key, account_name, directory=None)
        self.container = container
        self.connection_string = connection_string
        self.account_key = account_key
        self.account_name = account_name
        self.verbose = verbose
        self.checks()

    def checks(self):
        # check for Azure CLI, credentials and existence dir.
        self._check_azure_cli_installed()
        check_connection_credentials = self._check_connection_credentials()
        if not self.connection_string and not check_connection_credentials:
            self.connection_string = self._create_connection_string()

    def list_files(self):
        blob_service_client = BlobServiceClient.from_connection_string(
            os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        )
        container_client = blob_service_client.get_container_client(self.container)
        files = container_client.list_blobs()

        return files
