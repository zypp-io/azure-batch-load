import os
import pathlib

from setuptools.config.setupcfg import read_configuration


def get_config():
    repo_path = pathlib.Path(__file__).parent.parent.absolute()
    config_setup = read_configuration(os.path.join(repo_path, "setup.cfg"))
    config_requirements = config_setup["options"]["install_requires"]

    return config_requirements, repo_path


def check():
    config_requirements, repo_path = get_config()

    with open(os.path.join(repo_path, "requirements.txt")) as f:
        requirements_txt = f.read().splitlines()

    assert sorted(config_requirements) == sorted(requirements_txt), "Requirements are not equal"
    print("Requirements and setup.cfg and both are equal")


if __name__ == "__main__":
    check()
