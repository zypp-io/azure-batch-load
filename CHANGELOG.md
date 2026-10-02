Changelog
===


# 0.7.0, 01-10-2026

- Passwordless authentication: set only `AZURE_STORAGE_ACCOUNT` and azure-batch-load authenticates with
`DefaultAzureCredential` (`az login` locally, managed identity on Azure).
- `method="batch"` runs the Azure CLI with `--account-name` and `--auth-mode login` in passwordless mode.
- Download links are user delegation SAS URLs in passwordless mode, valid for at most 7 days.
- `expiry_download_links` has to be a positive number of days; it is checked when download links are created.
- `method="batch"` raises a `RuntimeError` when the Azure CLI command fails, instead of continuing silently.
- Connection strings are parsed per segment, so `AccountKey` can be the last segment. A connection string without
`AccountName` or `AccountKey` raises a clear `ValueError`.
- Connection string and account key keep working and take precedence when set.
- New dependency: `azure-identity`.


# 0.6.0, 21-08-2021

- Added `folder` argument in upload, so users can upload to specific folder in Azure Storage.
- Removed `pattern` flag in the CLI version of upload, reason for that is the new way of doing upload to a specific
folder in the Azure CLI is [`az storage fs directory`](https://docs.microsoft.com/en-us/cli/azure/storage/fs/directory?view=azure-cli-latest#az_storage_fs_directory_upload)
and this command does not have a pattern option opposed to
[`az storage blob upload-batch`](https://docs.microsoft.com/en-us/cli/azure/storage/blob?view=azure-cli-latest#az_storage_blob_upload_batch).
