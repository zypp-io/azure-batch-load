import os

from scripts.generic import get_config


def check():
    config_requirements, repo_path = get_config()

    with open(os.path.join(repo_path, "requirements.txt")) as f:
        requirements_txt = f.read().splitlines()

    assert sorted(config_requirements) == sorted(requirements_txt), "Requirements are not equal"
    print("Requirements and setup.cfg and both are equal")


if __name__ == "__main__":
    check()
