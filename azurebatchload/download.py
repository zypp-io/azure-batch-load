import logging
import os

from azure.storage.blob import BlobServiceClient

from azurebatchload.core import Base


class Download(Base):
    def __init__(
        self,
        destination,
        source,
        folder=None,
        extension=None,
        method="batch",
        modified_since=None,
        create_dir=True,
        list_files=None,
    ):
        super(Download, self).__init__(
            destination=destination,
            folder=folder,
            extension=extension,
            modified_since=modified_since,
            method=method,
            list_files=list_files,
        )
        self.checks()
        self.source = source
        if create_dir:
            if self.folder:
                self._create_dir(os.path.join(self.destination, self.folder))
            else:
                self._create_dir(self.destination)

    def _download_batch(self):
        pattern = self.define_pattern()

        cmd = f"az storage blob download-batch " f"-d {self.destination} " f"-s {self.source}"
        non_default = {
            "--connection-string": self.connection_string,
            "--pattern": pattern,
        }

        for flag, value in non_default.items():
            if value:
                cmd = f"{cmd} {flag} '{value}'"

        os.system(cmd)

    def _download_single(self):
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        container_client = blob_service_client.get_container_client(container=self.source)
        blob_list = container_client.list_blobs(name_starts_with=self.folder)

        n_files = 0
        for blob in blob_list:
            if self.extension and not blob.name.lower().endswith(self.extension.lower()):
                continue

            file_path, file_name = os.path.split(blob.name)

            if self.list_files and file_name not in self.list_files:
                continue
            blob_client = container_client.get_blob_client(blob=blob.name)
            directory = os.path.join(self.destination, file_path)
            directory = os.path.abspath(directory)
            self._create_dir(directory)
            logging.debug(f"Downloading file {blob.name}")
            with open(os.path.join(self.destination, blob.name), "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())

            n_files += 1

        logging.info(f"Downloaded total of {n_files} files")

    def download(self):

        # for batch load we use the Azure CLI
        if self.method == "batch":
            self._download_batch()

        # for single load we use Python SDK
        else:
            self._download_single()
