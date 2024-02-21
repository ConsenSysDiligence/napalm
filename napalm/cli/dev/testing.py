import click
from dataclasses import dataclass
from pathlib import Path
import re
from enum import Enum
from napalm.storage import get_storage_provider
from napalm.tool.run import run_tools


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


def _expected_findings(directory_path: Path):
    patterns = {
        TestType.detect: re.compile(r'napalm-detect: (\S+)'),
        TestType.ok: re.compile(r'napalm-ok: (\S+)'),
        TestType.wip_detect: re.compile(r'napalm-wip-detect: (\S+)'),
        TestType.wip_ok: re.compile(r'napalm-wip-ok: (\S+)')
    }

    findings = []

    for file_path in directory_path.rglob('*.sol'):
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
    collections = []
    semgrep_arguments = []
    workflow = None
    storage = get_storage_provider("pickle")
    run_tools(directory_path, collections, semgrep_arguments, workflow, storage, ai_filter)


@click.command(help="Run tests for this project")
def test():
    pass
