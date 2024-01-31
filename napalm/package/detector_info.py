from dataclasses import dataclass

from typing import List, Optional, Union, Any
from napalm.tool.semgrep_info import SemgrepConfiguration, SemgrepRule


@dataclass
class CompetitionInfo:
    name: str
    title: str


@dataclass
class DetectorInfo:
    id: str
    name: str

    short_description: str  # one liner
    long_description: str  # full description

    severity: str

    false_positive_prompt: Optional[str]

    base: Any

    twins: List[str]
    competitors: List[CompetitionInfo]

    @classmethod
    def from_semgrep(cls, semgrep_rule: SemgrepRule):
        competitors = (
            [
                CompetitionInfo(
                    name=competitor.get("name"),
                    title=competitor.get("title"),
                )
                for competitor in semgrep_rule.metadata.get("competitors", [])
            ]
            if semgrep_rule.metadata
            else []
        )
        return cls(
            id=semgrep_rule.id,
            name=semgrep_rule.id,
            short_description=semgrep_rule.message,
            long_description=semgrep_rule.message,
            severity=semgrep_rule.severity,
            base=semgrep_rule,
            false_positive_prompt=semgrep_rule.metadata.get("false_positive_prompt")
            if semgrep_rule.metadata
            else None,
            twins=semgrep_rule.metadata.get("twins", [])
            if semgrep_rule.metadata
            else [],
            competitors=competitors,
        )
