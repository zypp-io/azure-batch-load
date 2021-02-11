import logging
from azurebatchload.download import DownloadBatch
from azurebatchload.upload import UploadBatch

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d [%(levelname)-5s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
