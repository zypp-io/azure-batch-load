import setuptools.config


def check():
    config_setup = setuptools.config.read_configuration("../setup.cfg")
    requirements_setup = config_setup["options"]["install_requires"]

    with open("../requirements.txt") as f:
        requirements_txt = f.read().splitlines()

    assert sorted(requirements_setup) == sorted(requirements_txt)
