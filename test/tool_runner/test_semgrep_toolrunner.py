from napalm.tool.tool_runner import SemgrepToolRunner
from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)


def test_semgrep():
    tool_runner = SemgrepToolRunner(
        target_folder="test/tool/semgrep_test_dir/example_solidity.sol",
        configurations=["test/tool/semgrep_test_dir/example_config.yml"],
    )

    result = tool_runner.run_analysis()

    assert (
        result.runs[0].results[0].message.text
        == "Consider not casting block timestamp to ensure future functionality of the contract.\n"
    )
