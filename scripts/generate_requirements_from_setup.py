import os
import pathlib

from setuptools.config import read_configuration


def get_config():
    repo_path = pathlib.Path(__file__).parent.parent.absolute()
    config_setup = read_configuration(os.path.join(repo_path, "setup.cfg"))
    config_requirements = config_setup["options"]["install_requires"]

    return config_requirements, repo_path


def generate_requirements():
    config_requirements, repo_path = get_config()

    with open(os.path.join(repo_path, "requirements.txt"), "w") as f:
        f.write("\n".join(config_requirements))

    print(
        "Generated requirements.txt from setup.cfg, with the following requirements\n", "\n".join(config_requirements)
    )


if __name__ == "__main__":
    generate_requirements()
