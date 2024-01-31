from pathlib import Path

import yaml


def load_config():
    home = Path.home()
    napalm_home = home / ".napalm"
    napalm_home.mkdir(exist_ok=True)
    settings_file = napalm_home / "settings.yaml"

    return yaml.safe_load(settings_file.open("r"))


def update_config(config: dict):
    home = Path.home()
    napalm_home = home / ".napalm"
    napalm_home.mkdir(exist_ok=True)
    settings_file = napalm_home / "settings.yaml"

    with settings_file.open("w") as file:
        yaml.dump(config, file)


def load_local_config(dir: Path):
    config_file = dir / "configs" / "config.yaml"

    return yaml.safe_load(config_file.open("r"))
