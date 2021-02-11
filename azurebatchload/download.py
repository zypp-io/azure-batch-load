import os
from azurebatchload.checks import Checks


class DownloadBatch(Checks):
    def __init__(
        self,
        destination,
        source,
        connection_string=None,
        account_key=None,
        account_name=None,
        pattern=None,
        create_dir=True,
        verbose=False,
    ):
        super().__init__(connection_string, account_key, account_name, destination)
        self.destination = destination
        self.source = source
        self.connection_string = connection_string
        self.account_key = account_key
        self.account_name = account_name
        self.pattern = pattern
        self.create_dir = create_dir
        self.verbose = verbose

    def checks(self):
        # check for Azure CLI, credentials and existence dir.
        self._check_azure_cli_installed()
        check_connection_credentials = self._check_connection_credentials()
        if self.create_dir:
            self._create_dir()
        if not self.connection_string and not check_connection_credentials:
            self.connection_string = self._create_connection_string()

    def download(self):
        self.checks()

        cmd = f"az storage blob download-batch " f"-d {self.destination} " f"-s {self.source}"

        non_default = {
            "--connection-string": self.connection_string,
            "--pattern": self.pattern,
        }

        global_parameters = {"--verbose": self.verbose}

        for flag, value in non_default.items():
            if value:
                cmd = f"{cmd} {flag} '{value}'"

        for flag, value in global_parameters.items():
            if value:
                cmd = f"{cmd} {flag}"

        os.system(cmd)
