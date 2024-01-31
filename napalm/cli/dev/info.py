from operator import add
from pathlib import Path

import click
import toml
from rich.console import Console
from toolz.curried import pipe, filter, reduce, map, count

from napalm.package.collection_manager import CollectionManager


def get_package_name():
    pyproject_path = Path.cwd() / "pyproject.toml"
    if not pyproject_path.exists():
        raise FileNotFoundError(f"{pyproject_path} does not exist.")
    pyproject_content = toml.load(pyproject_path)
    package_name = pyproject_content.get("tool", {}).get("poetry", {}).get("name")
    if not package_name:
        raise ValueError("Package name not found in pyproject.toml.")
    return package_name


def _print_terminal_report(package_name, collections):
    console = Console()

    console.print(f"[cyan]{package_name}[/cyan] summary:")
    console.print(f"  - [green]{len(collections)}[/green] collections installed")
    console.print(
        f"  - [green]{count(reduce(add, map(lambda c: c.detectors, collections)))}[/green] detectors"
    )

    console.print(f"\n[cyan]{package_name}[/cyan] collections:")
    for collection in collections:
        console.print(
            f"  - [blue]{collection.collection_name}[/blue]"
            f" ([green]{len(collection.detectors)}[/green] detectors)"
        )

    for collection in collections:
        console.print(f"\n[cyan]{collection.collection_name}[/cyan] modules:")
        for detector in collection.detectors:
            console.print(
                f"  - [blue]{detector.id}[/blue] - [{detector.severity}]"
                f" [green]{detector.short_description.rstrip('\n')}[/green]"
            )


def _print_markdown_report(package_name, collections):
    """Print a markdown report to stdout."""
    console = Console()

    console.print(f"# :fire: Napalm Package: {package_name}")
    console.print(
        "This is an automatically generated report on the detectors in this package.\n"
    )

    console.print("Some quick stats:")
    console.print(f"  - {len(collections)} collections")
    console.print(
        f"  - {count(reduce(add, map(lambda c: c.detectors, collections)))} detectors"
    )

    # print table for each collection
    for collection in collections:
        console.print(f"\n## {collection.collection_name} modules:")
        console.print(f"  | ID | Description | Severity |")
        console.print(f"  | ------ | ----------- | -------- |")
        for detector in collection.detectors:
            console.print(
                f"  | {detector.id} | {detector.short_description.rstrip('\n')} | {detector.severity} |"
            )


@click.command(help="Print info on this project.")
@click.option("-m", "--markdown", "markdown", is_flag=True, default=False)
def info(markdown: bool):
    try:
        package_name = get_package_name()
    except Exception as e:
        click.echo(f"Error: {e}")
        exit(1)

    collection_manager = CollectionManager()

    collections = pipe(
        collection_manager.installed_collections(),
        filter(lambda c: c.startswith(f"{package_name}/")),
        map(collection_manager.get),
        filter(lambda c: c is not None),
        list,
    )

    if markdown:
        _print_markdown_report(package_name, collections)
    else:
        _print_terminal_report(package_name, collections)
