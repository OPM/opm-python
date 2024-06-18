import logging

from pathlib import Path
from opm_pypi_tools.constants import Directories, Filenames

class Helpers:
    @staticmethod
    def find_opm_common_so(project_dir: Path) -> str:
        dir_ = project_dir / Directories.opm
        return Helpers.find_file(dir_, "opmcommon_python*.so")

    @staticmethod
    def find_opm_simulators_so(project_dir: Path) -> str:
        dir_ = project_dir / Directories.opm / Directories.simulators
        return Helpers.find_file(dir_, "simulators*.so")

    @staticmethod
    def find_file(dir_: Path, pattern: str) -> str:
        files = list(dir_.glob(pattern))
        # Assume one and only one file is found
        if len(files) > 1:
            raise FileNotFoundError(f"More than one file matching {pattern} found in {dir_}")
        if len(files) == 0:
            raise FileNotFoundError(f"No files matching {pattern} found in {dir_}")
        filename = files[0].name
        return filename

    @staticmethod
    def generate_file_from_template(
        filename: Path, src_dir: Path, dest_dir: str, variables: dict[str,str]
    ) -> None:
        logging.info(f"Generating {filename} in {dest_dir}...")
        template = Helpers.read_template_file(src_dir / filename, variables)
        with open(dest_dir / filename, 'w', encoding='utf-8') as file:
            file.write(template)
        return

    @staticmethod
    def read_template_file(filename: Path, variables: dict[str,str]) -> str:
        with open(filename, 'r', encoding='utf-8') as file:
            template = file.read()
        # Replace placeholders with corresponding values from the dictionary
        for key, value in variables.items():
            placeholder = f"%%{key.upper()}%%"
            template = template.replace(placeholder, value)
        return template

