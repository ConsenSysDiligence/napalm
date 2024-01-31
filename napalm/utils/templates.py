from pathlib import Path

from jinja2 import Environment, PackageLoader, FileSystemLoader


def load_environment():
    """Load the Jinja2 environment with template directory"""
    try:
        # For package usage
        env = Environment(loader=PackageLoader("napalm", "templates"))
    except ValueError:
        # For local usage
        directory = Path(__file__).parent.parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(directory))

    return env


def render_and_save_template(
    env: Environment, template_name: str, dest_path: Path, variables: dict = None
):
    """Render a template and save it to a file"""
    template = env.get_template(template_name)
    config_content = template.render(
        variables or dict()
    )  # add any variables needed for rendering
    with dest_path.open("w") as file:
        file.write(config_content)
