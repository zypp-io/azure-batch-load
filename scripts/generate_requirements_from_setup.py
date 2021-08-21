import os

from scripts.generic import get_config


def generate_requirements():
    config_requirements, repo_path = get_config()

    with open(os.path.join(repo_path, "requirements.txt"), "w") as f:
        f.write("\n".join(config_requirements))

    print(
        "Generated requirements.txt from setup.cfg, with the following requirements\n", "\n".join(config_requirements)
    )


if __name__ == "__main__":
    generate_requirements()
