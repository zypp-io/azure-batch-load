Changelog
===


# 0.6.0, 21-08-2021

- Added `folder` argument in upload, so users can upload to specific folder in Azure Storage.
- Removed `pattern` flag in the CLI version of upload, reason for that is the new way of doing upload to a specific
folder in the Azure CLI is [`az storage fs directory`](https://docs.microsoft.com/en-us/cli/azure/storage/fs/directory?view=azure-cli-latest#az_storage_fs_directory_upload)
and this command does not have a pattern option opposed to
[`az storage blob upload-batch`](https://docs.microsoft.com/en-us/cli/azure/storage/blob?view=azure-cli-latest#az_storage_blob_upload_batch).
