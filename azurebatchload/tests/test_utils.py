import logging
import os

from dotenv import load_dotenv

from azurebatchload import Utils

load_dotenv()


def test_utils_download_links():
    logging.info("starting test for Utils - download links")
    utils = Utils(container=os.environ.get("CONTAINER"), create_download_links=True).list_blobs()
    logging.info(f"finished test with {utils.shape[0]} records")


if __name__ == "__main__":
    test_utils_download_links()
