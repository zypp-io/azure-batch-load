import logging
import os

from azure.storage.blob import BlobServiceClient

from azurebatchload.core import Base


class Upload(Base):
    def __init__(
        self,
        destination,
        source,
        folder=None,
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
            expiry_download_links=expiry_download_links,
        )
        self.blob_folder = folder
        self.overwrite = overwrite
        self.create_download_links = create_download_links

    def upload_batch(self):
        cmd = f"az storage fs directory upload " f"-f {self.destination} " f"-s {self.folder} -r"

        non_default = {"-d": self.blob_folder, "--connection-string": self.connection_string}

        for flag, value in non_default.items():
            if value:
                cmd = f"{cmd} {flag} '{value}'"

        os.system(cmd)

    def upload_single(self):
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
                if self.extension and os.path.isfile(full_path) and not file.lower().endswith(self.extension.lower()):
                    continue

                blob_folder = root.replace(self.folder, "").lstrip("/")

                if self.blob_folder:
                    # we only want to append blob_folder if it actually is a path or folder
                    # blob_folder can be empty string ""
                    if blob_folder:
                        blob_folder = os.path.join(self.blob_folder, blob_folder)
                    else:
                        blob_folder = self.blob_folder

                # if no folder is given, just upload to the container root path
                if not blob_folder:
                    container = self.destination
                else:
                    container = os.path.join(self.destination, blob_folder)
                container_client = blob_service_client.get_container_client(container=container)

                with open(full_path, "rb") as data:
                    logging.debug(f"Uploading blob {full_path}")
                    container_client.upload_blob(data=data, name=file, overwrite=self.overwrite)

                if self.create_download_links:
                    download_links[file] = self.create_blob_link(blob_folder=blob_folder, blob_name=file)

        return download_links

    def upload(self):
        self.checks()

        logging.info(f"Uploading to container {self.destination} with method = '{self.method}'.")
        if self.method == "batch":
            return self.upload_batch()
        else:
            return self.upload_single()
