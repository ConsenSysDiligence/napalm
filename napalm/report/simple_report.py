from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)
from rich.console import Console

console = Console()


class SimpleReporter:
    @staticmethod
    def report(report: Report):
        # report which tools were ran
        console.print(f"[green]Ran analysis using {len(report.runs)} tools[/green]")

        for run in report.runs:
            console.print(
                f"[cyan]Ran analysis using: \t{run.tool.driver.name}, with {len(run.tool.driver.rules)} rules[/cyan]"
            )

            for invocation in run.invocations:
                for notification in invocation.toolExecutionNotifications:
                    console.print(
                        f"[yellow]Tool Notification: {notification.message.text}[/yellow]"
                    )

        # print all issues found
        for run in report.runs:
            for finding in run.results:
                console.print(
                    f"[red]Found issue: {finding.message.text.rstrip('\n')}[/red]"
                )
