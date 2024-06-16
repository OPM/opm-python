import enum

class Directories:
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