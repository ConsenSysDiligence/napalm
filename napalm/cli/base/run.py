import os

import click
from toolz.curried import pipe, map, filter, reduce

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

from napalm.plugins.installed import get_installed_tool_plugins


def _get_twins(storage_provider):
    twin_storage = TwinStorage(storage_provider)

    collection_manager = CollectionManager()

    detectors = pipe(
        collection_manager.installed_collections(),
        map(collection_manager.get),
        filter(lambda m: m is not None),
        map(lambda m: m.detectors),
        reduce(lambda a, b: list(a) + list(b)),
    )
    collection_twins = twins_for_detectors(detectors)

    # REMARK: This implements naive merging of twin configurations.
    # Meaning that user configured twins A -> B + configured twins B -> C will NOT result in A -> B -> C
    return twin_storage.twins + collection_twins


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
    "--filter-level", default="Informational", help="Filter level for results."
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
    filter_level: str,
    ai_filter: bool,
    semgrep_arguments: str,
    **kwargs,
):
    # Get collections for workflow
    ctx.ensure_object(dict)

    plugin_tools = get_installed_tool_plugins()

    collection_manager = CollectionManager()
    workflow_storage = WorkflowStorage(ctx.obj["storage"])

    workflow_collections = workflow_storage.get_workflow(workflow)

    collections = []

    if workflow_collections is None or workflow_collections is False:
        click.echo(f"Workflow {workflow} does not exist")
        collection = collection_manager.get(workflow)

        if not collection:
            exit(0)

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

    # Configure analysis
    semgrep_runner = SemgrepToolRunner(
        target_folder=target,
        collections=collections,
        semgrep_arguments=semgrep_arguments,
    )
    semgrep_results = semgrep_runner.run_analysis(
        target, workflow, collections, **kwargs
    )

    plugin_reports = [
        plugin.tool_runner().run_analysis(target, workflow, collections, **kwargs)
        for plugin in plugin_tools
    ]

    merged_results = merge_reports(semgrep_results, *plugin_reports)

    if merged_results is None:
        click.echo("No results")
        exit(0)

    add_missing_snippets(merged_results)
    add_ids_to_locations(merged_results)
    add_location_relationships(merged_results)

    twins = _get_twins(ctx.obj["storage"])
    mark_duplicates_in_report(twins, merged_results)

    if ai_filter:
        filter_false_positives(merged_results)

    if merged_results is None:
        click.echo("No results")
        exit(0)

    # Print results
    match output:
        case "sarif":
            print(merged_results.model_dump_json(indent=4))
        case "markdown":
            markdown_report = render_markdown_report(merged_results)
            print(markdown_report)
        case "fancy":
            report(merged_results)
        case _:
            click.echo("Invalid output format")


for plugin in get_installed_tool_plugins():
    run = plugin.instrument_command(run)
