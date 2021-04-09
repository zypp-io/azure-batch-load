from pandas import DataFrame
from azure.storage.blob import BlobServiceClient
from azurebatchload.checks import Checks


class Utils(Checks):
    def __init__(
        self,
        container,
        dataframe=False,
        extended_info=False,
        connection_string=None,
        account_key=None,
        account_name=None,
        verbose=None,
    ):
        super().__init__(connection_string, account_key, account_name, directory=None)
        self.container = container
        self.dataframe = dataframe
        self.extended_info = extended_info
        self.connection_string = connection_string
        self.account_key = account_key
        self.account_name = account_name
        self.verbose = verbose
        self.checks()

    def checks(self):
        self.connection_string = self._check_connection_credentials()

    def list_files(self):
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        container_client = blob_service_client.get_container_client(self.container)
        files = container_client.list_blobs(name_starts_with="Productiviteit")

        included_info = ("name", "container", "last_modified", "size")
        # we have 4 options to return:
        # extended_info = False
        if not self.extended_info:
            # 1. dataframe = False, return just a list of file names
            if not self.dataframe:
                return [file.get("name") for file in files]
            # 2. dataframe = True, dataframe with one column filenames
            else:
                return DataFrame({"filename": [file.get("name") for file in files]})

        if self.extended_info:
            new_file_list = []
            for file in files:
                new_dict = {}
                for key, value in file.items():
                    if key in included_info:
                        new_dict[key] = file[key]
                new_file_list.append(new_dict)
            # 3. dataframe = False, return just a list of dicts
            if not self.dataframe:
                return new_file_list
            # 4. dataframe = True, return dataframe
            else:
                return DataFrame(new_file_list)
