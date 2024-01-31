from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
    PhysicalLocation,
    Result as Finding,
)
from rich.console import Console

console = Console()


def report(report: Report):
    _print_summary(report)

    # print all issues found
    for run in report.runs:
        for finding in run.results:
            _print_finding(finding)


def _print_summary(report: Report):
    console.print(f"[green]Ran {len(report.runs)} tools[/green]")

    for run in report.runs:
        console.print(
            f"[cyan]Ran analysis using: \t{run.tool.driver.name}, with {len(run.tool.driver.rules)} rules[/cyan]"
        )
        for invocation in run.invocations:
            for notification in invocation.toolExecutionNotifications:
                console.print(
                    f"[yellow]Tool Notification: {notification.message.text}[/yellow]"
                )

    if sum([len(run.results) for run in report.runs]) == 0:
        console.print("No issues found [green]0[/green]")
    else:
        console.print(
            f"Found [red]{sum([len(run.results) for run in report.runs])}[/red] issues:"
        )


def _print_finding(finding: Finding):
    # Note: the following is required as some tools put "Level." in front of the severity and some don't
    level = str(finding.level).lstrip("Level.")
    message = finding.message.text.rstrip("\n")

    # Check if the finding is a duplicate
    tags = finding.properties.tags or [] if finding.properties else []
    is_duplicate = "duplicate" in tags
    duplicate_label = "[DUP]" if is_duplicate else ""
    is_ai_false_positive = "ai_false_positive" in tags
    false_positive_label = "[magenta][FP][/magenta]" if is_ai_false_positive else ""

    match level:
        case "error":
            console.print(
                f"[red]Error[/red] {duplicate_label}{false_positive_label}: {message}"
            )
        case "warning":
            console.print(
                f"[yellow]Warning[/yellow] {duplicate_label}{false_positive_label}: {message}"
            )
        case "note":
            console.print(
                f"[blue]Note[/blue] {duplicate_label}{false_positive_label}: {message}"
            )
        case _:
            console.print(
                f"[white]{finding.level}[/white] {duplicate_label}{false_positive_label}: {message}"
            )

    for location in finding.locations:
        _print_location(location)


def _print_location(location: PhysicalLocation):
    start_line = location.physicalLocation.region.startLine
    end_line = location.physicalLocation.region.endLine
    line_range = f"{location.physicalLocation.region.startLine}"
    line_range = (
        f"{line_range}-{end_line}"
        if end_line and end_line != start_line
        else line_range
    )

    console.print(
        f"\t [blue]Location: {location.physicalLocation.artifactLocation.uri}#"
        f"{line_range}[/blue]"
    )

    if location.physicalLocation.region.snippet:
        console.print(
            "\n".join(
                [
                    f"\t[blue]| {line}[/blue]"
                    for line in location.physicalLocation.region.snippet.text.split(
                        "\n"
                    )
                ]
            )
        )
