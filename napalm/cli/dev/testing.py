import click
from dataclasses import dataclass
from pathlib import Path
import re
from enum import Enum


from typing import List
from napalm.storage import get_storage_provider
from napalm.tool.run import run_tools
from napalm.utils.workflow import get_collections_for_workflow
from napalm.package.collection_manager import CollectionManager
from pydantic_sarif.model import StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report
from pydantic_sarif.model import Result

from toolz import groupby
from rich.console import Console

import toml
from pathlib import Path


def get_package_name():
    # Construct the Path object for the pyproject.toml file
    pyproject_path = Path().cwd() / 'pyproject.toml'

    try:
        # Read the content of the pyproject.toml file
        pyproject_content = pyproject_path.read_text()

        # Parse the TOML content
        pyproject_data = toml.loads(pyproject_content)

        # Extract the entry point name
        entry_point_section = pyproject_data.get('tool', {}).get('poetry', {}).get('plugins', {}).get(
            'napalm.collection', {})
        entry_point_name = next(iter(entry_point_section.keys()), None)

        return entry_point_name

    except FileNotFoundError:
        print(f"Error: The file {pyproject_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


class TestType(Enum):
    detect = "napalm-detect"
    ok = "napalm-ok"
    wip_detect = "napalm-wip-detect"
    wip_ok = "napalm-wip-ok"


@dataclass
class ExpectedFinding:
    file: Path  # the file in which we expect to have a finding
    line: int  # the line number where we've added the annotation of the expected finding
    type: TestType  # the type of finding we expect to have (detect / ok / wip)
    detector_id: str  # the id of the detector that we expect to have a finding for

    discovered: bool = False  # whether we've found a matching finding in the report


def _expected_findings(directory_path: Path):
    patterns = {
        TestType.detect: re.compile(r'napalm-detect: (\S+)'),
        TestType.ok: re.compile(r'napalm-ok: (\S+)'),
        TestType.wip_detect: re.compile(r'napalm-wip-detect: (\S+)'),
        TestType.wip_ok: re.compile(r'napalm-wip-ok: (\S+)')
    }

    findings = []

    for file_path in (directory_path / "src").rglob('*.sol'):
        with file_path.open('r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                for test_type, pattern in patterns.items():
                    match = pattern.search(line)
                    if match:
                        finding = ExpectedFinding(
                            file=file_path,
                            line=line_number,
                            type=test_type,
                            detector_id=match.group(1)
                        )
                        findings.append(finding)

    return findings


def _run_tools(directory_path: Path, ai_filter: bool = False):
    # the directory is a foundry project and should work with all supported tools
    collection_manager = CollectionManager()
    package_name = get_package_name()
    workflow = f"{package_name}/*"

    collections = get_collections_for_workflow(get_storage_provider('pickle'), workflow)
    collections = list(
        filter(
            lambda a: a is not None,
            map(lambda c: collection_manager.get(c), collections),
        )
    )

    semgrep_arguments = []
    storage = get_storage_provider("pickle")

    return run_tools(directory_path, collections, semgrep_arguments, workflow, storage, ai_filter)


def _match_expectation_to_finding(expectation: ExpectedFinding, finding: Result):
    rule_id = finding.ruleId
    if re.match(r"\d-\d-.*", rule_id):
        rule_id = re.match(r"\d-\d-(.*)", rule_id).group(1)

    if not rule_id == expectation.detector_id:
        return False

    for location in finding.locations:
        if not str(expectation.file).endswith(location.physicalLocation.artifactLocation.uri):
            continue

        if location.physicalLocation.region.startLine not in (expectation.line, expectation.line + 1):
            continue
        return True

    return False


def _validate_findings(expected_findings: List[ExpectedFinding], report: Report):
    grouped_expectations = groupby(lambda expected: expected.detector_id, expected_findings)

    for run in report.runs:
        for finding in run.results:
            rule_id = finding.ruleId
            if re.match(r"\d-\d-.*", rule_id):
                rule_id = re.match(r"\d-\d-(.*)", rule_id).group(1)

            expectations = grouped_expectations.get(rule_id)
            if not expectations:
                continue

            for expectation in expectations:
                if _match_expectation_to_finding(expectation, finding):
                    expectation.discovered = True

    for expectation in expected_findings:
        if (expectation.type == TestType.detect or expectation.type == TestType.wip_detect) and not expectation.discovered:
            yield expectation
        elif (expectation.type == TestType.ok or expectation.type == TestType.wip_ok) and expectation.discovered:
            yield expectation


def _report(expectations: List[ExpectedFinding], missed_expectations: List[ExpectedFinding]):
    console = Console()

    console.print(f"Ran [green]{len(expectations)}[/green] tests.")

    if not missed_expectations:
        console.print("All tests passed!")
        return
    if missed_expectations:
        console.print(f"Missed [red]{len(missed_expectations)}[/red] tests!")

    for expectation in missed_expectations:
        # with color highlighting
        console.print(
            f"[red]{expectation.file}:{expectation.line} - {expectation.detector_id}[/red]"
        )


@click.command(help="Run tests for this project")
@click.option("--directory", type=click.Path(), default="./napalm_test/corpus")
def test(directory):
    # todo: assert that we're working with a napalm project
    directory = Path(directory)

    console = Console()
    if not directory.exists() or not directory.is_dir():
        console.print(f"Directory {directory} does not exist or is not a directory")
        exit(1)

    expectations = _expected_findings(directory)
    console.print(f"Running [green]{len(expectations)}[/green] tests!")

    report = _run_tools(directory)

    missed_expectations = _validate_findings(expectations, report)

    _report(expectations, list(missed_expectations))

    if any(expectation.type in (TestType.detect, TestType.ok) for expectation in missed_expectations):
        raise click.Abort("Tests failed!")
