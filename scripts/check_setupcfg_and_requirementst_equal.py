import os
import pathlib

import setuptools.config


def check():
    repo_path = pathlib.Path(__file__).parent.parent.absolute()
    print(repo_path)
    config_setup = setuptools.config.read_configuration(os.path.join(repo_path, "setup.cfg"))
    requirements_setup = config_setup["options"]["install_requires"]

    with open(os.path.join(repo_path, "requirements.txt")) as f:
        requirements_txt = f.read().splitlines()

    assert sorted(requirements_setup) == sorted(requirements_txt), "Requirements are not equal"
    print("Requirements and setup.cfg and both are equal")


if __name__ == "__main__":
    check()
