from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)


class ToolRunner:
    def run_analysis(self, target, workflow, collection, **kwargs) -> Report:
        pass
