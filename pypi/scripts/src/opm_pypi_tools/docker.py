import logging
import os
import subprocess
import sys

from pathlib import Path

from opm_pypi_tools.constants import DockerImageName

class DockerManager:
    def __init__(self, manylinux_name: DockerImageName, output_dir: Path) -> None:
        self.manylinux_name = manylinux_name
        self.docker_image_tag = self.manylinux_name.name + "-opm"
        self.output_dir = output_dir
        pass

    def build(self) -> None:
        # Use docker image inspect to check if the image exists, then build it if it doesn't
        try:
            result = subprocess.run(
                ["docker", "image", "inspect", self.docker_image_tag],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,  # Raise an exception if the process returns a non-zero exit code
            )
            logging.info(f"Docker image {self.docker_image_tag} already exists. Rebuilding..")
            self.build_image()
        except subprocess.CalledProcessError:
            logging.info(f"Docker image {self.docker_image_tag} does not exist. Building it...")
            self.build_image()
        except FileNotFoundError:
            print("Error: Docker not found.")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error checking Docker image: {e}")
            sys.exit(1)
        return

    def build_image(self) -> None:
        logging.info(f"Building Docker image {self.docker_image_tag}...")
        userid = str(os.getuid())
        groupid = str(os.getgid())
        docker_file_path = self.output_dir / "Dockerfile"
        build_context_path = self.output_dir
        try:
            result = subprocess.run(
                [
                    "docker", "build",
                    "--build-arg", f"HOST_UID={userid}",
                    "--build-arg", f"HOST_GID={groupid}",
                    "-t", self.docker_image_tag,
                    "-f", str(docker_file_path),
                    str(build_context_path)
                ],
                check=True,  # Raise an exception if the process returns a non-zero exit code
            )
            logging.info(f"Docker image {self.docker_image_tag} built successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error building Docker image: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: Docker not found.")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error building Docker image: {e}")
            sys.exit(1)
        return

    def run_build_in_container(self, python_version: str) -> None:
        logging.info(f"Running build in Docker container...")
        userid = str(os.getuid())
        groupid = str(os.getgid())
        try:
            result = subprocess.run(
                [
                    "docker", "run",
                    "--rm",
                    "--user", f"{userid}:{groupid}",
                    "-v", f"{self.output_dir}:/tmp/opm/opm-python",
                    self.docker_image_tag,
                    python_version
                ],
                check=True,  # Raise an exception if the process returns a non-zero exit code
            )
            logging.info(f"Build ran successfully in Docker container.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running build in Docker container: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: Docker not found.")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error running build in Docker container: {e}")
            sys.exit(1)
        return
