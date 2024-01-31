import subprocess
from typing import List

from loguru import logger
from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)
from toolz import reduce

from napalm.package.collection import Collection
from napalm.tool.tool_runner import ToolRunner
from typing import Optional


class SemgrepToolRunner(ToolRunner):
    def __init__(
        self,
        target_folder: str,
        collections: List[Collection],
        semgrep_arguments: Optional[str] = None,
    ):
        self.target_folder = target_folder
        self.collections = collections
        self.semgrep_arguments = semgrep_arguments or ""

    def _configurations(self):
        return list(
            reduce(
                lambda acc, c: acc + c.semgrep_configurations, self.collections, list()
            )
        )

    def run_analysis(self, target, workflow, collections, **kwargs):
        if not len(self._configurations()):
            logger.debug(f"no semgrep configurations in this collection")
            # There are now semgrep configurations in this collection, that's fine!
            return None

        logger.debug("Running semgrep")

        custom_arguments = (
            self.semgrep_arguments.split(" ") if self.semgrep_arguments else []
        )
        command = (
            ["semgrep"]
            + reduce(
                lambda acc, name: acc + ["--config", str(name)],
                self._configurations(),
                list(),
            )
            + custom_arguments
            + [self.target_folder]
            + ["--no-rewrite-rule-ids", "--sarif"]
        )
        logger.debug(f"Running semgrep with command: {command}")

        result = subprocess.run(command, capture_output=True, text=True)

        logger.debug("Finished running semgrep")

        if result.stderr:
            logger.debug(f"Semgrep Logs: \n{result.stderr}")

        if result.returncode != 0:
            logger.error(f"Error running semgrep: {result.stdout}")
            return None

        try:
            return Report.model_validate_json(result.stdout)
        except Exception as e:
            logger.error(f"Error parsing semgrep output: {e}")
            return None
