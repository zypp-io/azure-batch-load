"""
Passwordless smoke test against a real storage account.

Run from the repo root (az login first):
    uv run --no-project --with-editable . python scripts/smoke_test_passwordless.py <storage-account> <container>

Only touches blobs under a new smoke-<timestamp>/ prefix in the given container.
"""
import os
import shutil
import sys
import tempfile
import time
import urllib.request

from azure.identity import DefaultAzureCredential

from azurebatchload import Download, Upload, Utils

ACCOUNT, CONTAINER = sys.argv[1], sys.argv[2]
PREFIX = f"smoke-{time.strftime('%Y%m%d-%H%M%S')}"
FILES = {"a.pdf": b"smoke test a", "b.pdf": b"smoke test b", "note.txt": b"not a pdf"}

# passwordless only: no key may be picked up from the environment
for var in ("AZURE_STORAGE_CONNECTION_STRING", "AZURE_STORAGE_KEY"):
    os.environ.pop(var, None)
os.environ["AZURE_STORAGE_ACCOUNT"] = ACCOUNT

# fail fast: the storage SDK retries auth errors with backoff, which takes minutes per step
try:
    DefaultAzureCredential().get_token("https://storage.azure.com/.default")
except Exception as exc:
    sys.exit(f"No usable Azure login for storage. Run: az login --scope https://storage.azure.com/.default\n\n{exc}")

work = tempfile.mkdtemp(prefix="azurebatchload-smoke-")
source = os.path.join(work, "source")
os.makedirs(source)
for file_name, content in FILES.items():
    with open(os.path.join(source, file_name), "wb") as f:
        f.write(content)

results = []


def step(name, test):
    try:
        detail = test()
        results.append(True)
        print(f"PASS  {name}: {detail}")
    except Exception as exc:  # report every failure and keep going
        results.append(False)
        print(f"FAIL  {name}: {type(exc).__name__}: {exc}")


def fetch(url):
    # plain HTTP GET without credentials: only the SAS in the URL authorizes it
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def blob_names(folder):
    return Utils(container=CONTAINER, name_starts_with=f"{PREFIX}/{folder}/").list_blobs()


def downloaded_pdfs(destination):
    found = sorted(f for _, _, files in os.walk(destination) for f in files)
    assert found == ["a.pdf", "b.pdf"], f"downloaded {found}"
    return "a.pdf and b.pdf on disk"


def upload_single():
    links = Upload(
        destination=CONTAINER,
        source=source,
        folder=f"{PREFIX}/single",
        extension=".pdf",
        method="single",
        create_download_links=True,
        expiry_download_links=1,
    ).upload()
    assert sorted(links) == ["a.pdf", "b.pdf"], f"links for {sorted(links)}"
    assert fetch(links["a.pdf"]) == FILES["a.pdf"], "download link returned different content"
    return "2 blobs uploaded, download link returns the right content"


def list_blobs():
    names = blob_names("single")
    assert sorted(names) == [f"{PREFIX}/single/a.pdf", f"{PREFIX}/single/b.pdf"], f"listed {names}"
    return f"{len(names)} blobs listed"


def utils_links():
    links = Utils(
        container=CONTAINER, name_starts_with=f"{PREFIX}/single/", expiry_download_links=1
    ).create_blob_links()
    assert len(links) == 2, f"{len(links)} links"
    assert fetch(links[0]["url"]) in (FILES["a.pdf"], FILES["b.pdf"]), "download link returned different content"
    return "2 links, first one returns the right content"


def download_single():
    destination = os.path.join(work, "download-single")
    Download(
        destination=destination, source=CONTAINER, folder=f"{PREFIX}/single", extension=".pdf", method="single"
    ).download()
    return downloaded_pdfs(destination)


def download_batch():
    destination = os.path.join(work, "download-batch")
    download = Download(
        destination=destination, source=CONTAINER, folder=f"{PREFIX}/single", extension=".pdf", method="batch"
    )
    assert download.method == "batch", "Azure CLI not found, batch mode unavailable"
    download.download()
    return downloaded_pdfs(destination)


def upload_batch():
    upload = Upload(destination=CONTAINER, source=source, folder=f"{PREFIX}/batch", method="batch")
    assert upload.method == "batch", "Azure CLI not found, batch mode unavailable"
    upload.upload()
    pdfs = [name for name in blob_names("batch") if name.endswith(".pdf")]
    assert len(pdfs) == 2, f"{len(pdfs)} pdf blobs under {PREFIX}/batch/ (batch upload needs hierarchical namespace)"
    return "2 pdf blobs uploaded via az storage fs"


print(f"Account {ACCOUNT}, container {CONTAINER}, prefix {PREFIX}/\n")
step("upload single + download link", upload_single)
step("list blobs", list_blobs)
step("Utils.create_blob_links", utils_links)
step("download single", download_single)
step("download batch (az --auth-mode login)", download_batch)
step("upload batch (az --auth-mode login)", upload_batch)

shutil.rmtree(work, ignore_errors=True)
print(f"\n{sum(results)}/{len(results)} passed")
print("Remove the test blobs when done (permanent):")
print(f"  az storage fs directory delete -f {CONTAINER} -n {PREFIX} --account-name {ACCOUNT} --auth-mode login --yes")
print("Without hierarchical namespace:")
print(
    f"  az storage blob delete-batch -s {CONTAINER} --pattern '{PREFIX}/*' --account-name {ACCOUNT} --auth-mode login"
)
sys.exit(0 if all(results) else 1)
