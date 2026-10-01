import logging
import os
import re
from subprocess import STDOUT, CalledProcessError, check_output


class Checks:
    def __init__(self, directory):
        self.directory = directory

    @staticmethod
    def _create_connection_string():
        """
        When AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY are given,
        create an AZURE_STORAGE_CONNECTION_STRING

        Returns
        -------
        connection_string
        """
        base_string = (
            "DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};"
            "EndpointSuffix=core.windows.net"
        )
        connection_string = base_string.format(
            account_name=os.environ.get("AZURE_STORAGE_ACCOUNT", None),
            account_key=os.environ.get("AZURE_STORAGE_KEY", None),
        )

        return connection_string

    def _check_connection_credentials(self):
        """
        If connection string is given as env variable return it,
        else the connection string is generated from storage key and name.
        If only the storage account name is given, no connection string is returned
        and DefaultAzureCredential is used (passwordless).

        If none of the above are given, raise.

        Returns
        -------
        AZURE_STORAGE_CONNECTION_STRING (or None when passwordless), account name, account key
        """
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", None)
        account_name = os.environ.get("AZURE_STORAGE_ACCOUNT", None)
        account_key = os.environ.get("AZURE_STORAGE_KEY", None)

        if connection_string:
            account_name, account_key = self._parse_connection_string(connection_string)
            return os.environ.get("AZURE_STORAGE_CONNECTION_STRING"), account_name, account_key
        elif all([account_name, account_key]):
            return self._create_connection_string(), account_name, account_key
        elif account_name:
            return None, account_name, None
        else:
            # check for env variables else raise
            raise ValueError(
                "AZURE_STORAGE_ACCOUNT has to be set as env variable. "
                "Legacy: AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_KEY with AZURE_STORAGE_ACCOUNT."
            )

    def _check_dir(self):
        """
        When downloading files, create the given directory if it does not exist.

        Returns
        -------
        None
        """
        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"Source directory {self.directory} not found")

    def _create_dir(self, directory=None):
        """

        Parameters
        ----------
        directory

        Returns
        -------

        """
        if not directory:
            directory = self.directory

        if not os.path.exists(directory):
            logging.info(f"Destination {directory} does not exist, creating..")
            os.makedirs(directory)

    @staticmethod
    def _check_azure_cli_installed():
        try:
            check_output(["az", "--version"], stderr=STDOUT, shell=True)
            return True
        except CalledProcessError:
            logging.debug("Azure CLI is not installed, automatically setting method to 'single'")
            return False

    @staticmethod
    def _parse_connection_string(connection_string):
        account_name = re.search(r"AccountName=(.*?);", connection_string).group(1)
        account_key = re.search(r"AccountKey=(.*?);", connection_string).group(1)

        return account_name, account_key
