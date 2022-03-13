<p align="center">
  <img alt="logo" src="https://www.zypp.io/static/assets/img/logos/zypp/white/500px.png"  width="200"/>
</p>

[![Downloads](https://pepy.tech/badge/azurebatchload)](https://pepy.tech/project/azurebatchload)
![PyPI](https://img.shields.io/pypi/v/azurebatchload)
[![Open Source](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://opensource.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Azure Batch Load
High level Python wrapper for the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/) to download or upload files in batches from or to Azure Blob Storage Containers.
This project aims to be the [missing functionality](https://github.com/Azure/azure-storage-python/issues/554)
in the Python SDK of Azure Storage since there is no possibility to download or upload batches of files from or to containers.
The only option in the Azure Storage Python SDK is downloading file by file, which takes a lot of time.

Besides doing loads in batches, since version `0.0.5` it's possible to set method to `single` which will use the
[Azure Python SDK](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob) to process files one by one.


# Installation

```commandline
pip install azurebatchload
```

See [PyPi](https://pypi.org/project/azurebatchload/) for package index.

**Note**: For batch uploads (`method="batch"`) Azure CLI has to be [installed](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
and [configured](https://docs.microsoft.com/en-us/cli/azure/get-started-with-azure-cli).
Check if Azure CLI is installed through terminal:

```commandline
az --version
```

# Requirements

Azure Storage connection string has to be set as environment variable `AZURE_STORAGE_CONNECTION_STRING` or
the seperate environment variables `AZURE_STORAGE_KEY` and `AZURE_STORAGE_NAME` which will be used to create the connection string.

# Usage

## Download
### 1. Using the standard environment variables

Azure-batch-load automatically checks for environment variables: `AZURE_STORAGE_CONNECTION_STRING`,
   `AZURE_STORAGE_KEY`and `AZURE_STORAGE_ACCOUNT`.
So if the connection_string or storage_key + storage_account are set as environment variables,
   we can leave the argument `connection_string`, `account_key` and `account_name` empty:

```python
from azurebatchload import Download

Download(
   destination='../pdfs',
   source='blobcontainername',
   extension='.pdf'
).download()
```

### 2. Using `method="single"`

We can make skip the usage of the `Azure CLI` and just make use Python SDK by setting the `method="single"`:

```python
from azurebatchload import Download

Download(
   destination='../pdfs',
   source='blobcontainername',
   extension='.pdf',
   method='single'
).download()
```

### 3. Download a specific folder from a container

We can download a folder by setting the `folder` argument. This works both for `single` and `batch`.

```python
from azurebatchload import Download

Download(
   destination='../pdfs',
   source='blobcontainername',
   folder='uploads/invoices/',
   extension='.pdf',
   method='single'
).download()
```

### 4. Download a given list of files

We can give a list of files to download with the `list_files` argument.
Note, this only works with `method='single'`.

```python
from azurebatchload import Download

Download(
   destination='../pdfs',
   source='blobcontainername',
   folder='uploads/invoices/',
   list_files=["invoice1.pdf", "invoice2.pdf"],
   method='single'
).download()
```

## Upload:

### 1. Using the standard environment variables

```python
from azurebatchload import Upload

Upload(
   destination='blobcontainername',
   source='../pdf',
   extension='*.pdf'
).upload()
```

### 2. Using the `method="single"` method which does not require Azure CLI.

```python
from azurebatchload import Upload

Upload(
   destination='blobcontainername',
   source='../pdf',
   extension='*.pdf',
   method="single"
).upload()
```

### 3. Upload a given list of files with the `list_files` argument.

```python
from azurebatchload import Upload

Upload(
   destination='blobcontainername',
   source='../pdf',
   list_files=["invoice1.pdf", "invoice2.pdf"],
   method="single"
).upload()
```

## List blobs

With the `Utils.list_blobs` method we can do advanced listing of blobs in a container or specific folder in a container.
We have several argument we can use to define our scope of information:

- `name_starts_with`: This can be used to filter files with certain prefix, or to select certain folders: `name_starts_with=folder1/subfolder/lastfolder/`
- `dataframe`: Define if you want a pandas dataframe object returned for your information.
- `extended_info`: Get just the blob names or more extended information like size, creation date, modified date.

### 1. List a whole container with just the filenames as a list.
```python
from azurebatchload import Utils

list_blobs = Utils(container='containername').list_blobs()
```

### 2. List a whole container with just the filenames as a dataframe.
```python
from azurebatchload import Utils

df_blobs = Utils(
   container='containername',
   dataframe=True
).list_blobs()
```

### 3. List a folder in a container.
```python
from azurebatchload import Utils

list_blobs = Utils(
   container='containername',
   name_starts_with="foldername/"
).list_blobs()
```

### 4. Get extended information a folder.
```python
from azurebatchload import Utils

dict_blobs = Utils(
   container='containername',
   name_starts_with="foldername/",
   extended_info=True
).list_blobs()
```

### 5. Get extended information a folder returned as a pandas dataframe.
```python
from azurebatchload import Utils

df_blobs = Utils(
   container='containername',
   name_starts_with="foldername/",
   extended_info=True,
   dataframe=True
).list_blobs()
```
