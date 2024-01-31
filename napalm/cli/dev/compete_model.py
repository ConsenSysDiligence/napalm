from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class CompetitiveDetector(BaseModel):
    severity: str
    title: str
    description: Optional[str] = None
    # list of urls to publicly known reports from tool with findings for this detector
    reports: list[str] = Field(default_factory=list)


class CompetitiveTool(BaseModel):
    name: str
    reports: list[str] = Field(
        default_factory=list
    )  # list of urls to publicly known reports from tools
    url: Optional[str] = None  # url to tool's website

    detectors: List[CompetitiveDetector] = Field(default_factory=list)


class CompetitiveInfo(BaseModel):
    tools: List[CompetitiveTool] = Field(default_factory=list)


class BaseCompetitor(BaseModel):
    name: str
    title: str


class BaseToolInfo(BaseModel):
    id: str
    category: str
    competitors: List[BaseCompetitor] = Field(default_factory=list)


class BaseCompetitiveInfo(BaseModel):
    competing: Dict[str, List[BaseToolInfo]] = Field(default_factory=dict)
