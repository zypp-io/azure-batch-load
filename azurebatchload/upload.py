import os
from azure.storage.blob import BlobServiceClient
from azurebatchload.checks import Checks


class UploadBatch(Checks):
    def __init__(
        self,
        destination,
        folder=None,
        extension=None,
        connection_string=None,
        account_key=None,
        account_name=None,
        modified_date=None,
        verbose=False,
        method="batch",
    ):
        super().__init__(connection_string, account_key, account_name, folder)
        self.destination = destination
        self.folder = folder
        self.extension = extension
        self.connection_string = connection_string
        self.account_key = account_key
        self.account_name = account_name
        self.modified_date = modified_date
        self.verbose = verbose
        if not self._check_azure_cli_installed():
            self.method = "single"
        else:
            self.method = method

    def checks(self):
        self.connection_string = self._check_connection_credentials()
        self._check_dir()

        allowed_methods = ("batch", "single")
        if self.method not in allowed_methods:
            raise ValueError(
                f"Method {self.method} is not a valid method. "
                f"Choose from {' or '.join(allowed_methods)}."
            )

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

        if not new_extension.startswith("*"):
            new_extension = "*" + new_extension

        return new_extension

    def upload(self):
        self.checks()

        if self.method == "batch":
            pattern = self.create_not_case_sensitive_extension()
            cmd = f"az storage blob upload-batch " f"-d {self.destination} " f"-s {self.folder}"

            non_default = {"--connection-string": self.connection_string, "--pattern": pattern}
            global_parameters = {"--verbose": self.verbose}

            for flag, value in non_default.items():
                if value:
                    cmd = f"{cmd} {flag} '{value}'"

            for flag, value in global_parameters.items():
                if value:
                    cmd = f"{cmd} {flag}"

            os.system(cmd)
        else:
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            container_client = blob_service_client.get_container_client(container=self.destination)
            for file in os.listdir(self.folder):
                if file.lower().endswith(self.extension.lower()):
                    file_path = os.path.join(self.folder, file)
                    with open(file_path, "rb") as data:
                        container_client.upload_blob(data=data, name=file)
