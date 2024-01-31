from operator import add
from pathlib import Path

from pydantic_sarif.model import (
    PhysicalLocation,
    ArtifactContent,
    LocationRelationship,
)
from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)
from toolz.curried import reduce, map, pipe, groupby, filter, sorted, valmap, concat

from napalm.sarif.get import get_issues


def try_add_snippet_to_location(location: PhysicalLocation):
    file = Path(location.artifactLocation.uri)
    if not file.exists():
        return False

    start, end = location.region.startLine, location.region.endLine
    with file.open() as f:
        lines = f.readlines()
        location.region.snippet = ArtifactContent(
            text="".join(lines[start - 1 : end]).rstrip("\n")
        )


def add_missing_snippets(report: Report):
    for run in report.runs:
        for result in run.results:
            for location in result.locations:
                if location.physicalLocation.region.snippet is None:
                    try_add_snippet_to_location(location.physicalLocation)


def add_ids_to_locations(report: Report):
    """Adds ids to locations in the report"""
    issues = get_issues(report)
    locations = pipe(
        issues,
        map(lambda i: i.locations),
        concat,
    )
    for index, location in enumerate(locations):
        location.id = index


def add_location_relationships(report: Report):
    """Adds relationships between locations in the report

    currently only supports physical locations
    """
    issues = get_issues(report)

    file_locations_map = pipe(
        issues,
        map(lambda i: i.locations),
        concat,
        filter(lambda loc: loc.physicalLocation is not None),
        groupby(lambda loc: loc.physicalLocation.artifactLocation.uri),
        valmap(sorted(key=lambda loc: loc.physicalLocation.region.startLine)),
    )

    for _file, locations in file_locations_map.items():
        for index, location in enumerate(locations):
            next_location = locations[index + 1] if index + 1 < len(locations) else None
            if not next_location:
                continue

            if (
                next_location.physicalLocation.region.startLine
                > location.physicalLocation.region.endLine
            ):
                continue

            # the next location starts in the current location (overlap
            if (
                next_location.physicalLocation.region.endLine
                <= location.physicalLocation.region.endLine
            ):
                # includes
                location.relationships.append(
                    LocationRelationship(
                        target=next_location.id,
                        kinds=["includes"],
                    )
                )
                next_location.relationships.append(
                    LocationRelationship(
                        target=location.id,
                        kinds=["isIncludedBy"],
                    )
                )
            else:
                # overlap
                location.relationships.append(
                    LocationRelationship(
                        target=next_location.id,
                        kinds=["partialIncludes"],
                    )
                )
                next_location.relationships.append(
                    LocationRelationship(
                        target=location.id,
                        kinds=["partialIncludes"],
                    )
                )
