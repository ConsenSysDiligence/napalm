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
from napalm.analysis.filter import apply_filters
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


def run_tools(target, collections, semgrep_arguments, workflow, storage, ai_filter, **kwargs):
    # pull context
    workflow_storage = WorkflowStorage(storage)
    plugin_tools = get_installed_tool_plugins()

    semgrep_runner = SemgrepToolRunner(
        target_folder=target,
        collections=collections,
        semgrep_arguments=semgrep_arguments,
    )

    # run analysis
    semgrep_results = semgrep_runner.run_analysis(
        target, workflow, collections, **kwargs
    )

    plugin_reports = [
        plugin.tool_runner().run_analysis(target, workflow, collections, **kwargs)
        for plugin in plugin_tools
    ]

    # process analysis results
    merged_results = merge_reports(semgrep_results, *plugin_reports)

    if merged_results is None:
        click.echo("No results")
        exit(0)

    add_missing_snippets(merged_results)
    add_ids_to_locations(merged_results)
    add_location_relationships(merged_results)

    twins = _get_twins(storage)
    mark_duplicates_in_report(twins, merged_results)

    if ai_filter:
        filter_false_positives(merged_results)

    filters = workflow_storage.filters.get(workflow, {})
    if filters:
        apply_filters(merged_results, filters)

    return merged_results
