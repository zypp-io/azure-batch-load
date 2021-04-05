# Azure Batch Load
High level Python wrapper around the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/) to download or upload files in batches from or to Azure Blob Storage Containers. 
This project aims to be the [missing functionality](https://github.com/Azure/azure-storage-python/issues/554) 
in the Python SDK of Azure Storage since there is no possibility to download or upload batches of files from or to containers.
The only option in the Azure Storage Python SDK is downloading file by file, which takes a lot of time.

Besides doing loads in batches, since version `0.5.0` it's possible to set method to `single` which will use the 
Azure Python SDK to process files one by one.

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

DownloadBatch(
     destination='../pdfs',
     source='blobcontainername',
     extension='.pdf'
 ).download()
```

#### 2. Using `method="single"`

We can make skip the usage of the `Azure CLI` and just make use Python SDK by setting the `method="single"`:

```python
from azurebatchload import DownloadBatch

DownloadBatch(
   destination='../pdfs',
   source='blobcontainername',
   extension='.pdf',
   method='single'
)
```

#### 3. Download a specific folder from a container

We can download a folder by setting the `folder` argument. This works both for `single` and `batch`.

```python
from azurebatchload import DownloadBatch

DownloadBatch(
   destination='../pdfs',
   source='blobcontainername',
   folder='uploads/invoices/',
   extension='.pdf',
   method='single'
)
```

#### 4. Using own environment variables

If we use other names for the environment variables, we can define the arguments `connection_string`, `account_key` 
and `account_name` in our function:

```python
import os
from azurebatchload import DownloadBatch


DownloadBatch(
   destination='../pdfs',
   source='blobcontainername',
   connection_string=os.environ.get("connection_string"),
   extension='.pdf'
).download()
```

Or with key and name:

```python
import os
from azurebatchload import DownloadBatch


az_batch = DownloadBatch(
   destination='../pdfs',
   source='blobcontainername',
   account_key=os.environ.get("account_key"),
   account_name=os.environ.get("account_name"),
   extension='.pdf'
).download()
```

---

### Usage example upload:

#### 1. Using the standard environment variables

```python
import os
from azurebatchload import UploadBatch

UploadBatch(
   destination='blobcontainername',
   source='../pdf',
   pattern='*.pdf'
).upload()
```

---

For more information about file pattern matching in the `pattern` argument, see [Python Documentation](https://docs.python.org/3.7/library/fnmatch.html).