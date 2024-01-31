from operator import add
from typing import List, Set

from pydantic_sarif.model import Result
from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)
from toolz.curried import filter, map, pipe, reduce

from napalm.sarif.get import get_issues


def _mark_duplicate(base: Result, other: Result):
    """Mark duplicate in SARIF report"""
    base.properties = base.properties or {}
    base.properties["duplicate"] = True
    other.properties = other.properties or {}
    other.properties["duplicate"] = True


def _mark_duplicates_for_twin(twin: Set[str], sarif_report: Report):
    """Mark duplicates in SARIF report for a single twin"""
    issues: List[Result] = pipe(
        get_issues(sarif_report),
        filter(lambda issue: issue.ruleId in twin),
    )

    for index, issue in enumerate(issues):
        location_relation_ids = pipe(
            issue.locations,
            map(lambda loc: loc.relationships),
            reduce(add),
            filter(
                lambda rel: rel.kind in ("includes", "isIncludedBy", "partial-includes")
            ),
            map(lambda rel: rel.target),
            lambda e: set(e),
        )
        if not location_relation_ids:
            continue

        for next_issue in issues[index + 1 :]:
            next_location_ids = pipe(
                next_issue.locations,
                map(lambda loc: loc.id),
                list(),
            )
            if location_relation_ids.intersection(next_location_ids):
                _mark_duplicate(issue, next_issue)


def mark_duplicates_in_report(twins: List[Set[str]], sarif_report: Report):
    """Mark duplicates in SARIF report"""
    for twin in twins:
        _mark_duplicates_for_twin(twin, sarif_report)
