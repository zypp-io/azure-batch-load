import os


class DownloadBatch:
    def __init__(self, destination, source, account_key, account_name, pattern):
        self.destination = destination
        self.source = source
        self.account_key = account_key
        self.account_name = account_name
        self.pattern = pattern

    def download(self):
        os.system(
            f"az storage blob download-batch "
            f"-d {self.destination} "
            f"-s {self.source} "
            f"--account-name {self.account_name} "
            f"--account-key {self.account_key} "
            f"--pattern {self.pattern}"
        )


if __name__ == "__main__":
    key = "drlJSHUT3koBcNksnkF37ySg/gKioix+iaDCseFr814UNNHPUusmZw7v6VB7SxX1JXkyXlypgAj+Yy43kPigfg=="
    az_batch = DownloadBatch(
        destination="../pdfs",
        source="loonspecificaties",
        account_name="staffingassociates1",
        account_key=key,
        pattern="*.pdf",
    )
    az_batch.download()
