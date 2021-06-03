import logging
import os
from azure.storage.blob import BlobServiceClient
from azurebatchload.core import Base


class Upload(Base):
    def __init__(
        self,
        destination,
        source=None,
        extension=None,
        method="batch",
        modified_since=None,
        overwrite=False,
        list_files=None,
    ):
        super(Upload, self).__init__(
            destination=destination,
            folder=source,
            extension=extension,
            modified_since=modified_since,
            method=method,
            list_files=list_files,
        )
        self.overwrite = overwrite

    def upload(self):
        self.checks()

        if self.method == "batch":
            logging.info(f"Uploading to container {self.destination} method = 'batch'.")
            pattern = self.define_pattern().rsplit("/", 1)[-1]
            cmd = f"az storage blob upload-batch " f"-d {self.destination} " f"-s {self.folder}"

            non_default = {"--connection-string": self.connection_string, "--pattern": pattern}

            for flag, value in non_default.items():
                if value:
                    cmd = f"{cmd} {flag} '{value}'"

            os.system(cmd)
        else:
            logging.info(f"Uploading to container {self.destination} with method = 'single'.")
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

            for root, dirs, files in os.walk(self.folder):
                for file in files:

                    full_path = os.path.join(root, file)

                    # ignore hidden files
                    if file.startswith("."):
                        continue

                    # if list_files is given, only upload matched files
                    if self.list_files and file not in self.list_files:
                        continue

                    # if extension is given only upload if extension is matched
                    if (
                        self.extensions
                        and os.path.isfile(full_path)
                        and not file.lower().endswith(self.extensions.lower())
                    ):
                        continue

                    if self.destination in root:
                        blob_folder = root.split(self.destination)[1].lstrip("/")
                    else:
                        blob_folder = root.replace(self.folder, "").lstrip("/")

                    if len(blob_folder) == 0:
                        container = self.destination
                    else:
                        container = os.path.join(self.destination, blob_folder)
                    container_client = blob_service_client.get_container_client(
                        container=container
                    )
                    # if extensions is given, only upload matching files.

                    with open(full_path, "rb") as data:
                        logging.info(f"Uploading blob {full_path}")
                        container_client.upload_blob(data=data, name=file, overwrite=self.overwrite)
