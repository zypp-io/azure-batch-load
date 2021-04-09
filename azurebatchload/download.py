import os
import logging
from azure.storage.blob import BlobServiceClient
from azurebatchload.checks import Checks


class DownloadBatch(Checks):
    def __init__(
        self,
        destination,
        source,
        connection_string=None,
        account_key=None,
        account_name=None,
        folder=None,
        extension=None,
        method="batch",
        create_dir=True,
        verbose=False,
    ):
        super().__init__(connection_string, account_key, account_name, destination)
        self.destination = destination
        self.source = source
        self.connection_string = connection_string
        self.account_key = account_key
        self.account_name = account_name
        self.folder = folder
        self.extension = extension
        self.create_dir = create_dir
        self.verbose = verbose
        if not self._check_azure_cli_installed():
            self.method = "single"
        else:
            self.method = method

    def checks(self):
        self.connection_string = self._check_connection_credentials()
        if self.create_dir:
            self._create_dir()

        allowed_methods = ("batch", "single")
        if self.method not in allowed_methods:
            raise ValueError(
                f"Method {self.method} is not a valid method. "
                f"Choose from {' or '.join(allowed_methods)}."
            )

        if not self.folder.endswith("/"):
            self.folder = self.folder + "/"

    def define_pattern(self):
        if self.extension:
            self.extension = self.create_not_case_sensitive_extension()
        if self.folder and self.extension:
            pattern = self.folder + "*" + self.extension
        elif self.folder and not self.extension:
            pattern = self.folder + "*"
        elif not self.folder and self.extension:
            pattern = "*" + self.extension
        else:
            pattern = None

        return pattern

    def create_not_case_sensitive_extension(self):
        """
        We create in-case sensitive fnmatch
        .pdf -> .[Pp][Dd][Ff]
        .csv -> .[Cc][Ss][Vv]
        """
        new_extension = ""
        for letter in self.extension:
            if not letter.isalpha():
                new_extension += letter
            else:
                new_extension += f"[{letter.upper()}{letter}]"

        return new_extension

    def download(self):
        self.checks()

        # for batch load we use the Azure CLI
        if self.method == "batch":
            pattern = self.define_pattern()

            cmd = f"az storage blob download-batch " f"-d {self.destination} " f"-s {self.source}"
            non_default = {
                "--connection-string": self.connection_string,
                "--pattern": pattern,
            }

            global_parameters = {"--verbose": self.verbose}

            for flag, value in non_default.items():
                if value:
                    cmd = f"{cmd} {flag} '{value}'"

            for flag, value in global_parameters.items():
                if value:
                    cmd = f"{cmd} {flag}"

            os.system(cmd)
        # for single load we use Python SDK
        else:
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            container_client = blob_service_client.get_container_client(container=self.source)
            blob_list = container_client.list_blobs(name_starts_with=self.folder)
            for blob in blob_list:
                if self.extension and not blob.name.lower().endswith(self.extension.lower()):
                    continue
                blob_client = container_client.get_blob_client(blob=blob.name)

                directory = os.path.join(self.destination, blob.name.rsplit("/", 1)[0])
                directory = os.path.abspath(directory)
                self._create_dir(directory)
                logging.info(f"Downloading file {blob.name}")
                with open(os.path.join(self.destination, blob.name), "wb") as download_file:
                    download_file.write(blob_client.download_blob().readall())
