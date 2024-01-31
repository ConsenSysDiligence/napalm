from pathlib import Path

import click

from napalm.cli.dev.init.python_plugin_installer import PythonPluginInstaller


@click.command(help="Install the napalm project.")
@click.option(
    "-g",
    "--global",
    "global_install",
    is_flag=True,
    default=False,
    help="Install this napalm as global package.",
)
def install(global_install: bool):
    PythonPluginInstaller(Path.cwd() / "venv").install(global_install)
