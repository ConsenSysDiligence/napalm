from operator import add
from pathlib import Path

import click
import toml
from rich.console import Console
from toolz.curried import (
    pipe,
    filter,
    reduce,
    map,
    count,
    concat,
    groupby,
    valmap,
    itemmap,
    sorted,
)

from napalm.package.collection_manager import CollectionManager
import yaml
from pydantic import BaseModel, Field
from typing import Optional, List

from napalm.cli.dev.compete_model import (
    CompetitiveInfo,
    BaseCompetitiveInfo,
)


def get_package_name():
    pyproject_path = Path.cwd() / "pyproject.toml"
    if not pyproject_path.exists():
        raise FileNotFoundError(f"{pyproject_path} does not exist.")
    pyproject_content = toml.load(pyproject_path)
    package_name = pyproject_content.get("tool", {}).get("poetry", {}).get("name")
    if not package_name:
        raise ValueError("Package name not found in pyproject.toml.")
    return package_name


def _load_database(database_file: str):
    database_file = Path(database_file)
    database_file.touch()

    with database_file.open() as f:
        database = yaml.safe_load(f)

    return CompetitiveInfo.model_validate(database)


def _load_base_competitive_info(base_competitive_info_db: str) -> BaseCompetitiveInfo:
    base_competitive_info_db = Path(base_competitive_info_db)
    base_competitive_info_db.touch()

    with base_competitive_info_db.open() as f:
        database = yaml.safe_load(f)

    return BaseCompetitiveInfo.model_validate(database)


@click.command(help="Print competitive info on this project.")
@click.argument("competitive-info-db", type=click.Path())
@click.argument("base-competitive-info-db", type=click.Path())
@click.option("--verbose", "-v", is_flag=True, help="Print more information.")
def compete(competitive_info_db: str, base_competitive_info_db: str, verbose):
    try:
        package_name = get_package_name()
    except Exception as e:
        click.echo(f"Error: {e}")
        exit(1)

    competitive_info = _load_database(competitive_info_db)

    base_competitive_info = BaseCompetitiveInfo()
    if Path(base_competitive_info_db).exists():
        base_competitive_info = _load_base_competitive_info(base_competitive_info_db)

    collection_manager = CollectionManager()

    collections = pipe(
        collection_manager.installed_collections(),
        filter(lambda c: c.startswith(f"{package_name}/")),
        map(collection_manager.get),
        filter(lambda c: c is not None),
        list,
    )

    if len(collections) == 0:
        click.echo(f"No collections found for {package_name}.")
        exit(1)

    # covered_competition_detectors = {}
    # for collection in collections:
    #     for detector in collection.detectors:
    #         for competitor in detector.competitors:
    #             covered_competition_detectors[competitor.name, competitor.title] = detector

    covered_competition_detectors = pipe(
        collections,
        map(lambda collection: collection.detectors),
        concat,
        map(
            lambda detector: map(
                lambda competitor: ((competitor.name, competitor.title), detector),
                detector.competitors,
            )
        ),
        concat,
        dict,
    )

    base_covered_competition_detectors = pipe(
        base_competitive_info.competing.values(),
        concat,
        map(
            lambda detector: map(
                lambda competitor: ((competitor.name, competitor.title), detector.id),
                detector.competitors,
            )
        ),
        concat,
        dict,
    )

    covered_competition_detectors |= base_covered_competition_detectors

    # print information
    console = Console()

    console.print(f"# :fire: Napalm Package: {package_name}")
    console.print(
        "This is an automatically generated report on the detectors in this package.\n"
    )

    console.print("Some quick stats:")
    console.print(f"  - {len(collections)} collections")

    console.print(
        f"  - {count(reduce(add, map(lambda c: c.detectors, collections)))} detectors"
    )

    console.print(f" - {len(competitive_info.tools)} competitors")
    # print amount of competition detectors
    nr_competitive_detectors = count(
        concat(map(lambda t: t.detectors, competitive_info.tools))
    )
    console.print(f" - {nr_competitive_detectors} competition detectors")

    # print info for each competition tool, summarized by severity
    console.print(f"\n## Competition tools:")

    for tool in competitive_info.tools:
        console.print(f"\n### {tool.name}:")

        # print summary table
        console.print(f"  | Severity | Count | Covered |")
        console.print(f"  | -------- | ----- | ------- |")

        for severity, detectors in groupby(
            lambda d: d.severity, tool.detectors
        ).items():
            covered_by_package = pipe(
                detectors,
                map(lambda d: (tool.name, d.title)),
                filter(lambda d: d in covered_competition_detectors),
                count,
            )
            console.print(f"  | {severity} | {len(detectors)} | {covered_by_package} |")

        if not verbose:
            continue

        console.print(f"\n### {tool.name} uncovered detectors:")

        # print detailed table
        console.print(f"\n  | Severity | Title | covered |")
        console.print(f"  | -------- | ----- | ------- |")

        for detector in sorted(tool.detectors, key=lambda d: d.severity):
            covered = (tool.name, detector.title) in covered_competition_detectors
            if not covered:
                console.print(
                    f"  | {detector.severity} | {detector.title} | {covered} |"
                )
