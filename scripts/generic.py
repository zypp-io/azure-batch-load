import os
import pathlib

from setuptools.config import read_configuration


def get_config():
    repo_path = pathlib.Path(__file__).parent.parent.absolute()
    config_setup = read_configuration(os.path.join(repo_path, "setup.cfg"))
    config_requirements = config_setup["options"]["install_requires"]

    return config_requirements, repo_path
