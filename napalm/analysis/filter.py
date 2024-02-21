from toolz import pipe, map, filter, reduce
from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)
from napalm.package.collection_manager import CollectionManager


def _filter_severity(
    collection_manager: CollectionManager, report: Report, is_allow, severities
):
    for run in report.runs:
        run.results = list(
            filter(
                lambda result: result.level in severities
                if is_allow
                else result.level not in severities,
                run.results,
            )
        )


def _filter_confidence(
    collection_manager: CollectionManager, report: Report, is_allow, confidences
):
    for run in report.runs:
        for result in run.results:
            detector = collection_manager.get_detector(result.ruleId)
            if not detector or not detector.confidence:
                continue

            if detector.confidence not in confidences and is_allow:
                run.results.remove(result)
            elif detector.confidence in confidences and not is_allow:
                run.results.remove(result)


def apply_filters(report, filters):
    collection_manager = CollectionManager()
    # filters looks like {'severity': ('allow', ['High', 'Medium'])}
    for _type, values in filters.items():
        if not values:
            continue
        match _type:
            case "severity":
                allow_deny, severities = values
                _filter_severity(
                    collection_manager, report, allow_deny == "allow", severities
                )
            case "confidence":
                allow_deny, confidences = values
                _filter_confidence(
                    collection_manager, report, allow_deny == "allow", confidences
                )
            case "category":
                # not yet supported
                pass
            case _:
                pass
