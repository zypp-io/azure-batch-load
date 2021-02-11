# Azure Batch Load
High level Python wrapper around the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/) to download or upload files in batches from or to Azure Blob Storage Containers. 
This project aims to be the [missing functionality](https://github.com/Azure/azure-storage-python/issues/554) 
in the Python SDK of Azure Storage since there is no possibility to download or upload batches of files from or to containers.
The only option in the Azure Storage Python SDK is downloading file by file, which takes a lot of time.

**Note**: Azure CLI has to be [installed](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
and [configured](https://docs.microsoft.com/en-us/cli/azure/get-started-with-azure-cli).

Check if Azure CLI is installed through terminal:

```commandline
az --version
```

---

### Usage example Download:

#### 1. Using the standard environment variables

Azure-batch-load automatically checks for environment variables: `AZURE_STORAGE_CONNECTION_STRING`, 
   `AZURE_STORAGE_KEY`and `AZURE_STORAGE_ACCOUNT`. 
So if the connection_string or storage_key + storage_account are set as environment variables, 
   we can leave the argument `connection_string`, `account_key` and `account_name` empty:

```python
import os
from azurebatchload import DownloadBatch

if __name__ == '__main__':
    az_batch = DownloadBatch(
        destination='../pdfs',
        source='blobcontainername',
        pattern='*.pdf'
    )
    az_batch.download()
```

#### 2. Using own environment variables

If we use other names for the environment variables, we can define the arguments `connection_string`, `account_key` 
and `account_name` in our function:

```python
import os
from azurebatchload import DownloadBatch

if __name__ == '__main__':
    az_batch = DownloadBatch(
        destination='../pdfs',
        source='blobcontainername',
        connection_string=os.environ.get("connection_string"),
        pattern='*.pdf'
    )
    az_batch.download()
```

Or with key and name:

```python
import os
from azurebatchload import DownloadBatch

if __name__ == '__main__':
    az_batch = DownloadBatch(
        destination='../pdfs',
        source='blobcontainername',
        account_key=os.environ.get("account_key"),
        account_name=os.environ.get("account_name"),
        pattern='*.pdf'
    )
    az_batch.download()
```

---

### Usage example upload:

#### 1. Using the standard environment variables

```python
import os
from azurebatchload import UploadBatch

if __name__ == '__main__':
    az_batch = UploadBatch(
        destination='blobcontainername',
        source='../pdf',
        pattern='*.pdf'
    )
    az_batch.upload()

```

---

For more information about file pattern matching in the `pattern` argument, see [Python Documentation](https://docs.python.org/3.7/library/fnmatch.html).