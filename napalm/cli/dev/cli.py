import sys

import click
from loguru import logger

from napalm.cli.dev.info import info
from napalm.cli.dev.init import init
from napalm.cli.dev.install import install
from napalm.cli.dev.compete import compete
from napalm.cli.dev.testing import test
from napalm.storage import get_storage_provider


@click.group(help="Framework for running analysis on smart contracts.")
@click.option("--dev", is_flag=True, help="Run in development mode.")
@click.pass_context
def cli(ctx, dev: bool):
    if not dev:
        logger.remove()
        logger.add(sys.stderr, level="WARNING")

    ctx.ensure_object(dict)
    ctx.obj["storage"] = get_storage_provider("pickle")


cli.add_command(init)
cli.add_command(install)  # install napalm
cli.add_command(info)
cli.add_command(compete)
cli.add_command(test)

if __name__ == "__main__":
    cli()
