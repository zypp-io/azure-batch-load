import os
import logging


class DownloadBatch:
    def __init__(self, destination, source, account_key, account_name, pattern, create_dir=True):
        self.destination = destination
        self.source = source
        self.account_key = account_key
        self.account_name = account_name
        self.pattern = pattern
        self.create_dir = create_dir

    def download(self):

        if self.create_dir:
            self._create_dir()

        os.system(
            f"az storage blob download-batch "
            f"-d {self.destination} "
            f"-s {self.source} "
            f"--account-name {self.account_name} "
            f"--account-key {self.account_key} "
            f"--pattern {self.pattern}"
        )

    def _create_dir(self):
        if not os.path.exists(self.destination):
            logging.info(f"Destination {self.destination} does not exist, creating..")
            os.makedirs(self.destination)
        else:
            logging.info("Destination directory already exists, skipping")
