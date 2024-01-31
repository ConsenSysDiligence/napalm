from operator import add

from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)
from toolz.curried import map, pipe, reduce


def get_issues(report: Report):
    result = pipe(
        report.runs,
        map(lambda run: run.results),  # List[List[Result]]
        reduce(add),  # List[Result]
    )
    return list(result)
