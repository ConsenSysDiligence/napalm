import os

import click
from toolz.curried import pipe, map, filter, reduce

from napalm.tool.run import run_tools
from napalm.analysis.duplicate import mark_duplicates_in_report
from napalm.analysis.ai_false_positive import filter_false_positives
from napalm.package.collection import twins as twins_for_detectors
from napalm.package.collection_manager import CollectionManager
from napalm.report.fancy import report
from napalm.report.markdown_report import render as render_markdown_report
from napalm.sarif.location import (
    add_missing_snippets,
    add_ids_to_locations,
    add_location_relationships,
)
from napalm.storage import WorkflowStorage
from napalm.storage.twin import TwinStorage
from napalm.tool.semgrep_tool_runner import SemgrepToolRunner
from napalm.utils.sarif import merge_reports
from napalm.analysis.filter import apply_filters
from napalm.plugins.installed import get_installed_tool_plugins
from napalm.utils.workflow import get_collections_for_workflow

@click.command(help="Run analysis on smart contracts.")
@click.argument("workflow")
@click.argument("target")
@click.option(
    "--output",
    type=click.Choice(["markdown", "sarif", "fancy"]),
    default="fancy",
    help="Output format of the report",
)
@click.option(
    "--ai-filter", is_flag=True, help="Filter false positives using AI", type=click.BOOL
)
@click.option("--semgrep-arguments", help="Arguments to pass to semgrep", type=str)
@click.pass_context
def run(
    ctx,
    workflow: str,
    target: str,
    output: str,
    ai_filter: bool,
    semgrep_arguments: str,
    **kwargs,
):
    # Get collections for workflow
    ctx.ensure_object(dict)

    collection_manager = CollectionManager()
    workflow_collections = get_collections_for_workflow(ctx.obj["storage"], workflow)

    collections = []

    if workflow_collections is None or workflow_collections is False:
        click.echo(f"Workflow {workflow} does not exist")
        collection = collection_manager.get(workflow)

        if not collection:
            exit(0)

        # it's actually a collection!
        click.echo(f"Running analysis with the collection {workflow} instead!")
        collections = [collection]
    elif workflow_collections is []:
        click.echo(f"Workflow {workflow} is empty")
        exit(0)
    else:
        collections = list(
            filter(
                lambda a: a is not None,
                map(lambda c: collection_manager.get(c), workflow_collections),
            )
        )

    results = run_tools(
        target,
        collections,
        semgrep_arguments,
        workflow,
        ctx.obj["storage"],
        ai_filter,
        **kwargs,
    )

    if results is None:
        click.echo("No results")
        exit(0)

    # Print results
    match output:
        case "sarif":
            print(results.model_dump_json(indent=4))
        case "markdown":
            markdown_report = render_markdown_report(results)
            print(markdown_report)
        case "fancy":
            report(results)
        case _:
            click.echo("Invalid output format")


for plugin in get_installed_tool_plugins():
    run = plugin.instrument_command(run)
