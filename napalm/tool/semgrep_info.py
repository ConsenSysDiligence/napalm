from pathlib import Path
from typing import List, Any, Optional, Dict

import yaml
from pydantic import BaseModel, Field


class SemgrepRule(BaseModel):
    id: str
    message: str
    severity: str
    languages: Optional[List[str]]

    # we're ignoring the pattern fields because we're only interested in the metadata
    # pattern, patterns, pattern-either ...
    fix: Optional[Any] = None
    paths: Optional[Any] = None

    metadata: Optional[Dict[str, Any]] = None
    min_version: str = Field(None, alias="min-version")
    max_version: str = Field(None, alias="max-version")


class SemgrepConfiguration(BaseModel):
    rules: List[SemgrepRule]

    @classmethod
    def from_yaml(cls, file: Path):
        with file.open("r") as opened_file:
            data = yaml.safe_load(opened_file)
        return cls.model_validate(data)
