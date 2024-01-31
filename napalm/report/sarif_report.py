from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)


class SarifReporter:
    @staticmethod
    def render(report: Report):
        print(report.model_dump_json(indent=2))
