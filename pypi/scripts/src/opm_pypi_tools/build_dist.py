import logging
import os
import shutil
import subprocess
import sys

from pathlib import Path

from opm_pypi_tools.constants import Directories, DockerImageName
from opm_pypi_tools.docker import DockerManager
from opm_pypi_tools.helpers import Helpers

class BuildDist:
    def __init__(
        self,
        build_dir: str,
        source_dir: str,
        python_package_version: str,
        opm_version: str,
        output_dir: str,
        docker_image: DockerImageName|None
    ) -> None:
        self.build_dir = Path(build_dir).resolve()
        self.source_dir = Path(source_dir).resolve()
        self.template_dir = self.source_dir / Directories.pypi / Directories.templates / Directories.build
        self.opm_version = opm_version + python_package_version
        self.project_dir = self.build_dir / Directories.opm_python
        if not self.project_dir.exists():
            raise FileNotFoundError(f"Directory {self.project_dir} does not exist.")
        self.output_dir = Path(output_dir).resolve()
        self.docker_image = docker_image
        self.src_dir = self.project_dir / Directories.source

    def build(self):
        self.copy_source_files()
        self.opm_common_so_fn = Helpers.find_opm_common_so(self.output_dir)
        self.opm_simulators_so_fn = Helpers.find_opm_simulators_so(self.output_dir)
        self.generate_setup_py()
        self.generate_pyproject_toml()
        self.generate_readme()
        self.generate_license()
        self.generate_manifest()
        if self.docker_image is None:
            self.run_build_py()
        else:
            self.generate_dockerfile()
            self.generate_docker_build_script()
            self.maybe_build_docker_image()
            self.run_build_in_container()
        return

    def copy_file_to_output_dir(self, filename: str):
        logging.info(f"Copying {filename} to {self.output_dir}...")
        shutil.copy(self.template_dir / filename, self.output_dir / filename)
        return

    def copy_source_files(self):
        logging.info(f"Copying source files from {self.src_dir} to {self.output_dir}...")
        # We can assume that the source directory exists and that the output directory does not exist
        # This will copy the content of the source directory to the output directory,
        #  (but not the source directory itself)
        shutil.copytree(self.src_dir, self.output_dir)
        logging.info(f"Source files copied to {self.output_dir}.")
        return

    def generate_dockerfile(self):
        self.generate_file("Dockerfile", variables={
            "docker_image_name": self.docker_image.name
        })
        return

    def generate_docker_build_script(self):
        self.copy_file_to_output_dir("manylinux-build.sh")
        return

    def generate_file(self, filename: str, variables: dict):
        Helpers.generate_file_from_template(
            filename, src_dir=self.template_dir, dest_dir=self.output_dir, variables=variables
        )
        return

    def generate_license(self):
        self.copy_file_to_output_dir("LICENSE")
        return

    def generate_manifest(self):
        self.copy_file_to_output_dir("MANIFEST.in")
        return

    def generate_pyproject_toml(self):
        self.generate_file("pyproject.toml", variables={
            "opm_common_so": self.opm_common_so_fn,
            "opm_simulators_so": self.opm_simulators_so_fn,
            "package_version": self.opm_version,
        })
        return

    def generate_readme(self):
        self.copy_file_to_output_dir("README.md")
        return

    def generate_setup_py(self):
        self.copy_file_to_output_dir("setup.py")
        return

    def maybe_build_docker_image(self):
        self.docker_manager = DockerManager(self.docker_image, self.output_dir)
        self.docker_manager.build()
        return

    def run_build_in_container(self):
        #for python_version in ["cp38-cp38", "cp39-cp39", "cp310-cp310", "cp311-cp311", "cp312-cp312"]:
        for python_version in ["cp311-cp311"]:
            self.docker_manager.run_build_in_container(python_version)
        return

    def run_build_py(self):
        # Run "WHEEL_PLAT_NAME=manylinux2014_x86_64 python3 -m build --sdist --wheel"
        env = os.environ.copy()
        env["WHEEL_PLAT_NAME"] = "manylinux2014_x86_64"
        try:
            result = subprocess.run(
                [
                    sys.executable,  # Use the same python3 interpreter that is running this script
                    "-m",
                    "build",
                    "--sdist",
                    "--wheel",
                ],
                cwd=self.output_dir,
                check=True,  # Raise an exception if the process returns a non-zero exit code
                env=env
            )
            logging.info(f"'python -m build ..' ran successfully in {self.output_dir}.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running build.py: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: build.py not found.")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error running build.py: {e}")
            sys.exit(1)
        return
