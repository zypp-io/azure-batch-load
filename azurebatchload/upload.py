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
    ):
        super(Upload, self).__init__(
            destination=destination,
            folder=source,
            extension=extension,
            modified_since=modified_since,
            method=method,
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
            logging.info(f"Uploading container {self.destination} with method = 'single'.")
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

            for root, dirs, files in os.walk(self.folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    container_client = blob_service_client.get_container_client(
                        container=os.path.join(self.destination, full_path)
                    )
                    # if extensions is given, only upload matching files.
                    if (
                        self.extension
                        and os.path.isfile(full_path)
                        and file.lower().endswith(self.extension.lower())
                    ):
                        with open(full_path, "rb") as data:
                            logging.info(f"Uploading blob {full_path}")
                            container_client.upload_blob(
                                data=data, name=file, overwrite=self.overwrite
                            )
                    else:
                        if not file.startswith("."):
                            with open(full_path, "rb") as data:
                                logging.info(f"Uploading blob {full_path}")
                                container_client.upload_blob(
                                    data=data, name=file, overwrite=self.overwrite
                                )
