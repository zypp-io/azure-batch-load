import logging
from azurebatchload.download import Download
from azurebatchload.upload import Upload
from azurebatchload.utils import Utils


logging.basicConfig(
    format="%(asctime)s.%(msecs)03d [%(levelname)-5s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
