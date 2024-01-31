import click
import rich
from toolz import filter, count

from napalm.package.collection_manager import CollectionManager
from napalm.tool.semgrep_info import SemgrepRule
from napalm.plugins.installed import get_installed_tool_plugins


@click.group(help="View info on installed collections")
@click.pass_context
def collections(ctx):
    pass


@collections.command(help="List all installed collections")
@click.pass_context
def list(ctx):
    collection_manager = CollectionManager()

    click.echo("Installed collections:")
    for collection in collection_manager.installed_collections():
        click.echo(f"  - {collection}")


@collections.command(help="Show info on a collection")
@click.argument("collection")
@click.pass_context
def show(ctx, collection: str):
    console = rich.console.Console()

    collection_manager = CollectionManager()
    collection_name = collection
    collection = collection_manager.get(collection_name)

    if not collection:
        console.print(f"Collection [red]{collection_name}[/red] not found!")
        exit(0)

    detectors = collection.detectors
    semgrep_rules = count(
        filter(lambda d: isinstance(d.base, SemgrepRule), collection.detectors)
    )
    tool_rules = dict()
    for plugin in get_installed_tool_plugins():
        tool_rules[plugin.tool_name()] = count(
            collection.plugin_detectors.get(plugin.tool_name(), [])
        )
    tool_rules["semgrep"] = semgrep_rules

    for detector in detectors:
        console.print(
            f"[blue]{detector.id}[/blue] - [{detector.severity}] [green]{detector.short_description.rstrip('\n')}[/green]"
        )

    # summary
    console.print(f"\n[blue]{collection_name}[/blue] summary:")
    for tool, rules in tool_rules.items():
        console.print(f"  - [green]{rules}[/green] {tool} rules")
