import os
import logging
from subprocess import check_output, CalledProcessError, STDOUT


class Checks:
    def __init__(self, connection_string, account_key, account_name, directory):
        self.connection_string = connection_string
        self.account_key = (account_key,)
        self.account_name = account_name
        self.directory = directory

    def _create_connection_string(self):

        base_string = (
            "DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};"
            "EndpointSuffix=core.windows.net"
        )

        if self.account_name and self.account_key:
            connection_string = base_string.format(self.account_name, self.account_key)
        else:
            connection_string = base_string.format(
                account_name=os.environ.get("AZURE_STORAGE_ACCOUNT", None), account_key=os.environ.get("AZURE_STORAGE_KEY", None)
            )

        return connection_string

    def _check_connection_credentials(self):
        if self.connection_string:
            return self.connection_string
        if os.environ.get("AZURE_STORAGE_CONNECTION_STRING", None):
            return os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        elif all([self.account_key, self.account_name]) or all(
            [os.environ.get("AZURE_STORAGE_KEY", None), os.environ.get("AZURE_STORAGE_ACCOUNT", None)]
        ):
            return self._create_connection_string()
        else:
            # if account_key and account_name arguments are not set,
            #   check for env variables else raise
            raise ValueError(
                "If account_key and account_name are not given as argument "
                "they have to be specified as environment variables named "
                " AZURE_STORAGE_KEY and AZURE_STORAGE_ACCOUNT"
            )

    def _check_dir(self):
        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"Source directory {self.directory} not found")

    def _create_dir(self, directory=None):
        if not directory:
            directory = self.directory

        if not os.path.exists(directory):
            logging.info(f"Destination {directory} does not exist, creating..")
            os.makedirs(directory)
        else:
            logging.info("Destination directory already exists, skipping")

    @staticmethod
    def _check_azure_cli_installed():
        try:
            check_output(["az", "--version"], stderr=STDOUT, shell=True)
            return True
        except CalledProcessError:
            logging.warning("Azure CLI is not installed, automatically setting method to 'single'")
            return False
