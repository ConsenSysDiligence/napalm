from toolz import pipe, map, filter, reduce
from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)


def _filter_severity(report: Report, is_allow, severities):
    for run in report.runs:
        run.results = list(
            filter(
                lambda result: result.level in severities
                if is_allow
                else result.level not in severities,
                run.results,
            )
        )


def _filter_confidence(report: Report, is_allow, confidences):
    for run in report.runs:
        run.results = list(
            filter(
                lambda result: result.properties.get("precision", "none") in confidences
                if is_allow
                else result.confidence not in confidences,
                run.results,
            )
        )


def _apply_filters(report, filters):
    # filters looks like {'severity': ('allow', ['High', 'Medium'])}
    for _type, values in filters.items():
        match _type:
            case "severity":
                allow_deny, severities = values
                _filter_severity(report, allow_deny == "allow", severities)
            case "confidence":
                # not yet supported
                pass
            case "category":
                # not yet supported
                pass
            case _:
                pass
