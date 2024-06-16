from setuptools import setup

# NOTE: The parameters to setup() are given in the pyproject.toml file
#   We do not use "python setup.py sdist bdist_wheel" to build the package distribution
#   as it is deprecated in favor of "python -m build .."
#   The "python -m build .." will call setup() with the parameters from the
#   pyproject.toml file
#   This setup.py file only serves as fallback for older tools that do not support
#   the pyproject.toml file
setup()
