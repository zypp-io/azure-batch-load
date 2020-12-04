# azure-batch
Module to download files in batches from Azure Blob Storage Container. This project aims to be the [missing functionality](https://github.com/Azure/azure-storage-python/issues/554) 
in the Python SDK of Azure Storage. There is no possibility to download batches of files from containers, so the only option for now is downloading file by file, which takes a lot of time.

Note: Azure CLI has to be installed, [downloadlink](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).

Usage example:

```python
from azurebatch import DownloadBatch

if __name__ == '__main__':
    key = 'ajh;sdhjhgjasdKioix+iaDSAJfafjh;waasd3k'
    az_batch = DownloadBatch(
        destination='../pdfs',
        source='blobcontainername',
        account_name='storageaccountname',
        account_key=key,
        pattern='*.pdf'
    )
    az_batch.download()
```

For more information about file pattern matching in the `pattern` argument, see [Python Documentation](https://docs.python.org/3.7/library/fnmatch.html).