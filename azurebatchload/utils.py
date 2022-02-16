from ntpath import basename

from azure.storage.blob import BlobServiceClient
from pandas import DataFrame

from azurebatchload.core import Base


class Utils(Base):
    def __init__(
        self,
        container,
        name_starts_with=None,
        dataframe=False,
        extended_info=False,
        create_download_links=False,
        expiry_download_links=7,
    ):
        super(Utils, self).__init__(
            destination=container,
            folder=name_starts_with,
            expiry_download_links=expiry_download_links,
        )

        self.container = container
        self.name_starts_with = name_starts_with
        self.dataframe = dataframe
        self.extended_info = extended_info
        self.connection_string = self._check_connection_credentials()[0]
        self.create_download_links = create_download_links
        self._blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self._container_client = self._blob_service_client.get_container_client(self.container)

    ###################
    # private methods #
    ###################

    def _get_files(self):
        files = self._container_client.list_blobs(name_starts_with=self.name_starts_with)
        return files

    @staticmethod
    def _get_file_names_simple(files):
        return [file.get("name") for file in files]

    def _list_blobs_not_extended(self, files):

        file_names = self._get_file_names_simple(files)
        # 1. dataframe = False, return just a list of file names
        if not self.dataframe:
            return file_names
        # 2. dataframe = True, dataframe with one column filenames
        else:
            return DataFrame({"filename": file_names})

    def _list_blobs_extended(self, files):
        included_info = ("name", "container", "last_modified", "creation_time", "size")
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

    ##################
    # public methods #
    ##################

    def list_blobs(self):
        files = self._get_files()
        if not self.extended_info:
            return self._list_blobs_not_extended(files)
        else:
            return self._list_blobs_extended(files)

    def create_blob_links(self):
        files = self._get_file_names_simple(self._get_files())
        url_list = []
        for file in files:
            url = self.create_blob_link(blob_folder=file.replace("/" + basename(file), ""), blob_name=basename(file))
            url_list.append({"filename": file, "url": url})

        if self.dataframe:
            return DataFrame(url_list)
        else:
            return url_list
