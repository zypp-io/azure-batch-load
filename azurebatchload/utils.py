from azure.storage.blob import BlobServiceClient
from pandas import DataFrame

from azurebatchload.checks import Checks


class Utils(Checks):
    def __init__(
        self,
        container,
        name_starts_with=None,
        dataframe=False,
        extended_info=False,
    ):
        super(Utils, self).__init__(directory=None)
        self.container = container
        self.name_starts_with = name_starts_with
        self.dataframe = dataframe
        self.extended_info = extended_info
        self.connection_string = self._check_connection_credentials()[0]

    def list_blobs(self):
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        container_client = blob_service_client.get_container_client(self.container)
        files = container_client.list_blobs(name_starts_with=self.name_starts_with)

        included_info = ("name", "container", "last_modified", "creation_time", "size")
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
                df = DataFrame(new_file_list)
                df = df.reindex(columns=included_info)
                # convert size to mb
                df["size"] = (df["size"] / 1_000_000).round(2)
                df = df.rename(columns={"size": "size_mb"})
                return df


def convert_windows_path_to_unix(path: str) -> str:
    """
    If users provide an windows, we convert it to unix path

    Parameters
    ----------
    path: str
        Given destination path

    Returns
    -------
    Path converted to unix style.
    """
    return path.replace(r"\\", "/").replace("\\", "/")
