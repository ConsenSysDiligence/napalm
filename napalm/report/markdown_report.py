from dataclasses import dataclass
from typing import List, Optional

from pydantic_sarif.model import ReportingDescriptor as SarifRule
from pydantic_sarif.model import Result as SarifIssue
from pydantic_sarif.model import (
    StaticAnalysisResultsFormatSarifVersion210JsonSchema as Report,
)
from toolz.curried import pipe, map, reduce, groupby

from napalm.utils.templates import load_environment


@dataclass
class Issue:
    id: str
    rule_id: str
    title: str
    location_string: Optional[str]
    description: str
    severity: str
    suggestions: List[str]
    snippets: List[str]
    references: List[str]
    instances: int

    @classmethod
    def from_sarif(cls, sarif_issue: SarifIssue):
        severity_string = str(sarif_issue.level).lstrip("Level.").lstrip("l.")
        snippets = []
        for location in sarif_issue.locations:
            if location.physicalLocation.region.snippet is not None:
                location_string = f"// {location.physicalLocation.artifactLocation.uri}#{location.physicalLocation.region.startLine}"
                snippets.append(
                    f"{location_string}\n{location.physicalLocation.region.snippet.text}"
                )

        return cls(
            id=sarif_issue.guid,
            rule_id=sarif_issue.ruleId,
            title=str(sarif_issue.ruleId),
            location_string=None,
            severity=severity_string,
            description=str(sarif_issue.message.text),
            suggestions=[],
            snippets=snippets,
            references=[],
            instances=len(sarif_issue.locations),
        )


@dataclass
class Rule:
    report_id: Optional[str]
    id: str
    name: str
    short_description: str
    full_description: Optional[str]
    help: Optional[str]
    issues: List[Issue]
    number_of_issues: int
    severity: Optional[str]

    @classmethod
    def from_sarif(cls, sarif_rule: SarifRule):
        return cls(
            report_id=None,
            id=sarif_rule.id,
            name=sarif_rule.name,
            short_description=sarif_rule.shortDescription.text,
            full_description=sarif_rule.fullDescription.text
            if sarif_rule.fullDescription
            else None,
            help=sarif_rule.help.text if sarif_rule.help else None,
            issues=[],
            number_of_issues=0,
            severity=None,
        )


def assign_ids(rules: List[Rule]):
    counters = {"high": 0, "medium": 0, "warning": 0, "low": 0}
    for rule in rules:
        counters[rule.severity] += 1
        rule.report_id = f"{rule.severity[0].upper()}-{counters[rule.severity]:02}"
    return rules


def _max_severity(issues):
    severity_order = {"high": 4, "medium": 3, "warning": 2, "low": 1}
    reverse = {v: k for k, v in severity_order.items()}
    return reverse.get(max([severity_order[issue.severity] for issue in issues]))


def render(report: Report):
    environment = load_environment()

    template = environment.get_template("report/simple_report.md.jinja2")

    issues = pipe(
        report.runs,
        map(lambda run: run.results),  # get all results
        reduce(lambda a, b: a + b),  # flatten
        map(Issue.from_sarif),  # convert to issues
        groupby(lambda issue: issue.rule_id),  # group by id -> {rule_id: [issues], ...}
    )

    rules = pipe(
        report.runs,
        map(lambda run: run.tool.driver.rules),  # get all rules
        reduce(lambda a, b: a + b),  # flatten
        map(Rule.from_sarif),  # convert to rules
    )

    rules = {rule.id: rule for rule in rules}
    for rule_id, issues in issues.items():
        rules[rule_id].issues = issues
        rules[rule_id].number_of_issues = len(issues)
        rules[rule_id].severity = _max_severity(issues)

    assign_ids(rules.values())
    rules = groupby(lambda rule: rule.severity, rules.values())

    markdown_report = template.render(
        dict(
            report_description="NAPALM Static Analysis Report",
            issues=issues,
            result_summaries=[],
            rules=rules,
        )
    )

    return markdown_report
