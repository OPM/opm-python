import logging

from pathlib import Path

import click
from opm_pypi_tools.build_dist import BuildDist
from opm_pypi_tools.build_opm import BuildOPM
from opm_pypi_tools.constants import DockerImageName, PythonVersion

@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """``opm-pypi-tools`` provides a set of tools for generating and uploading
    OPM Python packages to PyPI. The following subcommands are available:

    * ``build``: Build the OPM Python source distribution and wheel.
    """

    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        #logging.basicConfig(level=logging.WARNING)

@main.command()
@click.option(
    '--build-dir',
    required=True,
    help='Path to the opm-python build directory')
@click.option(
    '--source-dir',
    required=True,
    help='Path to the opm-python source directory')
@click.option(
    '--python-package-version',
    required=False,
    default='',
    help='Version of the OPM Python package. This version is appended to the end of the opm-version. So if opm-version="2024.04" and the value of this option is ".1" it will result in a Python package version of "2024.04.1". The default value is the empty string')
@click.option(
    '--opm-version',
    required=True,
    help='Version of OPM, e.g., "2024.04"')
@click.option(
    '--output-dir',
    required=True,
    help='Path to the output directory. This directory should not already exists, but its parent directory must exist. The directory will be created, then the source files will be copied to this directory, and finally the distribution files will be generated here.')
@click.option('--docker', is_flag=True, help='Use a Docker manylinux image to build the distribution. The default value is True. If this option is not provided, the distribution will be built using the current environment.')
@click.option('--docker-image', default='manylinux2014_x86_64', required=False, help='When using a docker image, specify the type of image to use. The default value is "manylinux2014". If the --docker option is not provided, this option is ignored.')
def build(
    build_dir: str,
    source_dir: str,
    python_package_version: str,
    opm_version: str,
    output_dir: str,
    docker: bool,
    docker_image: str
    ) -> None:
    """Builds the OPM Python source distribution and wheels for a set of Python versions."""
    # Check if the provided path exists and is a directory
    if not (Path(build_dir).exists() and Path(build_dir).is_dir()):
        click.echo('Error: The provided build dir path does not exist or is not a directory.')
        return
    if not (Path(source_dir).exists() and Path(source_dir).is_dir()):
        click.echo('Error: The provided source dir path does not exist or is not a directory.')
        return
    output_dir_ = Path(output_dir).resolve()
    if output_dir_.exists():
        click.echo('Error: The provided output directory path already exists.')
        return
    if not output_dir_.parent.exists():
        click.echo('Error: The parent directory of the provided output directory does not exist.')
        return
    if docker:
        try:
            docker_image = DockerImageName[docker_image.lower()]
        except ValueError:
            raise ValueError(f"Invalid value for docker image name: {docker_image}.")
    else:
        docker_image = None
    logging.info(f"Building OPM Python wheel package in {build_dir}...")
    BuildDist(
        build_dir,
        source_dir,
        python_package_version,
        opm_version,
        output_dir,
        docker_image).build()

@main.command()
@click.option(
    '--source-dir',
    required=True,
    help='Path to the opm-python source directory')
@click.option(
    '--python-version',
    required=True,
    help='Python version to use when building opm-common in the manylinux docker container. The value should be a string in the format "X.Y" where X is the major version and Y is the minor version, e.g., "3.9". Minimum supported version is 3.8.')
@click.option(
    '--docker-tag-extension',
    required=True,
    help='Docker image tag extension. The generated docker image is assigned a tag according to the following template: "manylinux2014_x86_64-opm-python{python-version}{tag-extension}". This tag can be used later when pulling the image to build opm-python in a manylinux docker container.')
def build_opm(source_dir: str, python_version: str, docker_tag_extension: str) -> None:
    """Builds opm-common, opm-grid, opm-models, opm-simulators inside
    a manylinux docker container. Each module is installed to /opt/opm inside the container.
    Finally, all build artifacts are deleted (except for the /opt/opm directory) to reduce the size of the image."""
    python_version = PythonVersion.from_str(python_version)
    if not (Path(source_dir).exists() and Path(source_dir).is_dir()):
        click.echo('Error: The provided source dir path does not exist or is not a directory.')
        return
    logging.info(f"Building opm-common, opm-grid, opm-models, and opm-simulators in docker container...")
    docker_tag = f"manylinux2014_x86_64-opm-python{python_version}{docker_tag_extension}"
    BuildOPM(
        source_dir, python_version, docker_tag
    ).build()

if __name__ == "__main__":
    main()