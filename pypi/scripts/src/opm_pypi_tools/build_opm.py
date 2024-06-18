import logging
import os
import shutil
import subprocess
import sys
import tempfile

from pathlib import Path

from opm_pypi_tools.constants import Directories, PythonVersion
from opm_pypi_tools.helpers import Helpers

class BuildOPM:
    def __init__(self, source_dir: str, python_version: PythonVersion, docker_tag: str) -> None:
        self.python_version = python_version
        self.docker_tag = docker_tag
        self.source_dir = Path(source_dir).resolve()
        self.template_dir = self.source_dir / Directories.pypi / Directories.templates / Directories.build_opm

    def build(self) -> None:
        self.build_dir = self.generate_temp_build_dir()
        self.generate_dockerfile()
        self.generate_user_config_jam()
        self.generate_entrypoint_script()
        self.build_docker_image()
# docker build --build-arg HOST_UID=$(id -u) --build-arg HOST_GID=$(id -g) -t manylinux2014-opm -f Dockerfile .
    def build_docker_image(self) -> None:
        logging.info(f"Building Docker image {self.docker_tag}...")
        try:
            result = subprocess.run(
                [
                    "docker", "build",
                    "--build-arg", f"HOST_UID={os.getuid()}",  # Get the user ID of the current user
                    "--build-arg", f"HOST_GID={os.getgid()}",  # Get the group ID of the current user
                    "-t", self.docker_tag,
                    "-f",
                    str(self.build_dir / "Dockerfile"),
                    str(self.build_dir)
                ],
                check=True,  # Raise an exception if the process returns a non-zero exit code
            )
            logging.info(f"Docker image {self.docker_tag} built successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error building Docker image: {e}")
            sys.exit(1)
        return

    def copy_file_to_build_dir(self, filename: str):
        logging.info(f"Copying {filename} to {self.build_dir}...")
        shutil.copy(self.template_dir / filename, self.build_dir / filename)
        return

    def generate_dockerfile(self) -> None:
        self.copy_file_to_build_dir("Dockerfile")
        return

    def generate_entrypoint_script(self) -> None:
        self.copy_file_to_build_dir("entrypoint.sh")
        return

    def generate_file(self, filename: str, variables: dict):
        Helpers.generate_file_from_template(
            filename, src_dir=self.template_dir, dest_dir=self.build_dir, variables=variables
        )
        return

    def generate_temp_build_dir(self) -> Path:
        logging.info("Generating temporary build directory...")
        # Create a directory in /tmp for the Dockerfile and other build files
        build_dir = Path(tempfile.mkdtemp(prefix="opm-python-"))
        logging.info(f"Temporary build directory {build_dir} created.")
        return build_dir

    def generate_user_config_jam(self) -> None:
        self.generate_file("user-config.jam", variables={
            "python_version": str(self.python_version),
            "python_version_long": f"{self.python_version}.0",
        })
        return
