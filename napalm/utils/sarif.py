from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)


def merge_reports(*reports: Report) -> Report:
    """Merge two reports into one.

    Args:
        base (Report): The base report to merge into.
        other (Report): The report to merge into the base report.

    Returns:
        Report: The merged report.
    """
    reports = list(filter(lambda r: r is not None, reports))

    if len(reports) == 0:
        return None
    if len(reports) == 1:
        return reports[0]

    # we can get away with a shallow copy because we only update top level fields
    copy = reports[0].model_copy()

    for i in range(1, len(reports)):
        copy.runs += reports[i].runs

    return copy
