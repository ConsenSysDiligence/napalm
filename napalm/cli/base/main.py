import sys

import click
from loguru import logger

from napalm.storage import get_storage_provider
from .auto import auto_install_hook
from .collection import collections
from .run import run
from .twin import twins
from .workflow import workflow, workflows


@click.group(help="Framework for running analysis on smart contracts.")
@click.option("--dev", is_flag=True, help="Run in development mode.")
@click.pass_context
def cli(ctx, dev: bool):
    if not dev:
        logger.remove()
        logger.add(sys.stderr, level="WARNING")

    ctx.ensure_object(dict)
    ctx.obj["storage"] = get_storage_provider("pickle")

    auto_install_hook(ctx.obj["storage"])


cli.add_command(run)
cli.add_command(workflow)  # manage an individual workflow
cli.add_command(workflows)  # manage workflows
cli.add_command(collections)  # manage collections
cli.add_command(twins)  # manage twins


if __name__ == "__main__":
    cli()
