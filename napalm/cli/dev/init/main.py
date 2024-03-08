import venv
from pathlib import Path

import click
import git
import loguru

from napalm.cli.dev.init.python_plugin_installer import PythonPluginInstaller
from napalm.utils.templates import load_environment, render_and_save_template
from napalm.plugins.installed import get_installed_tool_plugins

import re


def to_snake_case(text):
    # Replace all non-word characters with a space
    text = re.sub(r'[^\w\s]', ' ', text)

    # Convert to lowercase and split by whitespace characters
    words = text.lower().split()

    # Join the words with underscores
    snake_case = '_'.join(words)

    return snake_case


def initialize_git_repo():
    try:
        # Initialize a new Git repository in the current directory
        git.Repo.init("")
        print("Git repository initialized successfully.")
    except Exception as e:
        print(f"An error occurred while initializing the Git repository: {e}")


def setup_sample_detectors(module_name: str):
    module = Path(module_name)
    module.mkdir(exist_ok=True)
    (module / "__init__.py").touch()

    # set up directory structure
    (module / "detectors").mkdir()
    (module / "detectors" / "__init__.py").touch()
    (module / "indicators").mkdir()
    (module / "indicators" / "__init__.py").touch()
    (module / "optimisations").mkdir()
    (module / "optimisations" / "__init__.py").touch()

    (module.parent / "napalm_test").mkdir()
    (module.parent / "napalm_test" / "corpus").mkdir()

    # copy sample detectors
    sample_directory = (
        Path(__file__).parent.parent.parent.parent.parent / "templates" / "init"
    )

    for plugin in get_installed_tool_plugins():
        plugin.initialize_default_files(module)

    semgrep_file = (module / "detectors") / "semgrep_example_rule.yml"
    semgrep_template = sample_directory / "example_semgrep_rule.yml"

    semgrep_file.write_text(semgrep_template.read_text())


@click.command(help="Initiate a napalm project")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Force init on a non-empty directory",
)
@click.option(
    "-g",
    "--global",
    "global_install",
    is_flag=True,
    default=False,
    help="Install this napalm as global package.",
)
def init(force: bool, global_install: bool):
    # check if the current directory is empty
    if any(Path.cwd().iterdir()) and not force:
        loguru.logger.warning(
            "Cannot run init on a non-empty directory, use --force to override"
        )
        exit(1)

    module_name = to_snake_case(Path.cwd().name)

    # initialise virtual environment
    loguru.logger.info("Initialising virtual environment")
    venv.create(Path.cwd() / "venv", with_pip=True)

    loguru.logger.info("Populating directory structure")
    # initialise git
    initialize_git_repo()

    # setup gitignore and readme
    env = load_environment()

    detectors_file = Path(".gitignore")
    readme_file = Path("README.md")

    render_and_save_template(env, "init/README.md", readme_file)
    render_and_save_template(env, "init/.gitignore", detectors_file)

    # set up sample detectors
    loguru.logger.info("Setting up sample detectors")
    setup_sample_detectors(module_name)

    # set up pyproject.toml
    pytoml = Path("pyproject.toml")

    # write to the files
    env = load_environment()
    render_and_save_template(
        env, "install/pyproject.toml.jinja2", pytoml, {"module_name": module_name}
    )
    napalm_entry_point = Path().cwd() / module_name / "napalm.py"
    render_and_save_template(
        env,
        "init/napalm.py.jinja2",
        napalm_entry_point,
        {"module_name": module_name},
    )

    # install napalm modules
    loguru.logger.info("Installing napalm modules")

    installer = PythonPluginInstaller(Path.cwd() / "venv")
    installer.install(global_install)
