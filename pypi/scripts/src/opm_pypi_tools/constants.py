import enum

class Directories:
    build = "build"
    build_opm = "build-opm"
    docs = "docs"
    opm = "opm"
    opm_python = "opm-python"
    pypi = "pypi"
    simulators = "simulators"
    source = "src"
    templates = "templates"

class DockerImageName(enum.Enum):
    manylinux2014_x86_64 = 0

class Filenames:
    readme = "README.md"

class PythonVersion(enum.Enum):
    v3_8 = 0
    v3_9 = 1
    v3_10 = 2
    v3_11 = 3
    v3_12 = 4

    @classmethod
    def from_str(cls, version_str):
        try:
            return cls[f"v{version_str.replace('.', '_')}"]
        except KeyError:
            valid_versions = ', '.join([str(version) for version in cls])
            raise ValueError(f"Invalid python version: {version_str}, valid versions are {valid_versions}")

    def __str__(self):
        # Return the version in the desired format (e.g., "3.8" instead of "v3_8")
        return self.name[1:].replace('_', '.')