from azurebatchload.checks import Checks


class Base(Checks):
    def __init__(
        self,
        destination,
        folder,
        extension=None,
        modified_since=None,
        method="batch",
        list_files=None,
    ):
        super().__init__(directory=folder)

        self.destination = destination
        self.folder = folder
        self.extension = extension
        self.extensions = extension
        self.modified_since = modified_since
        if not self._check_azure_cli_installed():
            self.method = "single"
        else:
            self.method = method
        self.list_files = list_files
        credentials = self._check_connection_credentials()
        self.connection_string = credentials[0]
        self.account_name = credentials[1]
        self.account_key = credentials[2]

    def checks(self):
        allowed_methods = ("batch", "single")
        if self.method not in allowed_methods:
            raise ValueError(f"Method {self.method} is not a valid method. Choose from {' or '.join(allowed_methods)}.")

        if self.list_files and self.method == "batch":
            raise ValueError("list_files is only allowed with method='single'.")

        if self.list_files and not isinstance(self.list_files, list):
            raise ValueError(f"Argument list_files was set, but is not of type list, but type {type(self.list_files)}")
