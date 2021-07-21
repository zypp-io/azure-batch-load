import logging
import os
from datetime import datetime, timedelta

from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas

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
        create_download_links=False,
        expiry_download_links=7,
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
        self.create_download_links = create_download_links
        self.expiry_download_links = expiry_download_links

    def create_blob_link(self, blob_folder, blob_name):
        if blob_folder:
            full_path_blob = f"{blob_folder}/{blob_name}"
        else:
            full_path_blob = blob_name
        url = f"https://{self.account_name}.blob.core.windows.net/{self.destination}/{full_path_blob}"
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            account_key=self.account_key,
            container_name=self.destination,
            blob_name=full_path_blob,
            permission=BlobSasPermissions(read=True, delete_previous_version=False),
            expiry=datetime.utcnow() + timedelta(days=self.expiry_download_links),
        )

        url_with_sas = f"{url}?{sas_token}"
        return url_with_sas

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
            download_links = {}

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
                    container_client = blob_service_client.get_container_client(container=container)
                    # if extensions is given, only upload matching files.

                    with open(full_path, "rb") as data:
                        logging.info(f"Uploading blob {full_path}")
                        container_client.upload_blob(data=data, name=file, overwrite=self.overwrite)

                    if self.create_download_links:
                        download_links[file] = self.create_blob_link(blob_folder=blob_folder, blob_name=file)
                    else:
                        download_links = None

            return download_links
