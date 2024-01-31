import subprocess
from pathlib import Path


class PythonPluginInstaller:
    def __init__(self, virtual_env_path):
        self.venv_path = virtual_env_path

    def _is_venv_setup(self):
        venv_path = Path(self.venv_path)

        # Check the activation script based on the operating system
        activate_script = venv_path / "bin" / "activate"

        # Return True if the activation script exists, False otherwise
        return activate_script.exists()

    def install_package(self, global_install: bool = False):
        """Install the package in editable mode"""
        if not global_install:
            if not self._is_venv_setup():
                # Create the virtual environment
                raise Exception("Virtual environment not setup")

            # Activate the virtual environment
            activate_script = f"{self.venv_path}/bin/activate"
            activate_command = f"source {activate_script}"

            # Combine the activation with the install command
            command = f"{activate_command} && pip install --editable ."
        else:
            command = "pip install --editable ."

        # Execute the command
        result = subprocess.run(command, shell=True, capture_output=True)

        if result.returncode != 0:
            raise Exception(f"Error installing package: {result.stderr}")

    def install(self, global_install: bool = False):
        self.install_package(global_install)
