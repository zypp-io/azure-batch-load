import logging

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d [%(levelname)-5s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
