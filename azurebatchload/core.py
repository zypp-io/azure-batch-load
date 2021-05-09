from azurebatchload.checks import Checks


class Base(Checks):
    def __init__(self, destination, folder, extension=None, modified_since=None, method="batch"):
        super().__init__(directory=folder)

        self.destination = destination
        self.folder = folder
        if extension:
            self.extension = self.create_not_case_sensitive_extension(extension)
        else:
            self.extension = extension
        self.extensions = extension
        self.modified_since = modified_since
        if not self._check_azure_cli_installed():
            self.method = "single"
        else:
            self.method = method
        self.connection_string = self._check_connection_credentials()

    def checks(self):
        allowed_methods = ("batch", "single")
        if self.method not in allowed_methods:
            raise ValueError(
                f"Method {self.method} is not a valid method. "
                f"Choose from {' or '.join(allowed_methods)}."
            )

    @staticmethod
    def create_not_case_sensitive_extension(extension):
        """
        We create in-case sensitive fnmatch
        .pdf -> .[Pp][Dd][Ff]
        .csv -> .[Cc][Ss][Vv]
        """
        new_extension = ""
        for letter in extension:
            if not letter.isalpha():
                new_extension += letter
            else:
                new_extension += f"[{letter.upper()}{letter}]"

        if not new_extension.startswith("*"):
            new_extension = "*" + new_extension

        return new_extension

    def define_pattern(self):
        if self.folder and not self.extension:
            if self.folder.endswith("/"):
                pattern = self.folder + "*"
            else:
                pattern = self.folder + "/*"
        elif self.folder and self.extension:
            pattern = self.folder.rstrip("/") + "/" + "*" + self.extension
        elif not self.folder and self.extension:
            pattern = "*" + self.extension
        else:
            pattern = None

        return pattern
