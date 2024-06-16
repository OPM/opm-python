#!/bin/bash

# This script expects to be run with a "docker run --user ..." command line such that
# the script is run with the same user as on the host system. The same user should
# also have sudo permissions without password inside the container (this should already
# have been set up by the Dockerfile and the "docker build --build-arg ..." command line).
#
# The user should also have read/write access to the directory opm-python within the
# current directory in the container, which is a just a mount of the current directory (when
# "docker run" was executed) on the host.
# This mount should already have been set up in the "docker run -v ..." command line.
#
# Since opm-python directory should contain the opm-python project files,
# the purpose of this script is to build a wheel from that distribution.

# Expect a single command line argument: The python version to use on the form
#  used by the manylinux images, e.g. "cp38-cp38".
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <python version>"
    exit 1
fi
python_version=$1
# Activate the correct python version by putting it first in the PATH
export PATH=/opt/python/"$python_version"/bin:$PATH
python -m venv .venv  # Avoid installing python packages globally
source .venv/bin/activate
python -m ensurepip --upgrade
pip install --upgrade pip
pip install pipx
# Add pipx installed commands to the PATH
export PATH=$HOME/.local/bin:$PATH
pipx install poetry
pip install build auditwheel
cd opm-python # This is the directory containing the opm-python project files on the host
#WHEEL_PLAT_NAME=manylinux2014_x86_64 python -m build --wheel --sdist .
WHEEL_PLAT_NAME=manylinux2014_x86_64 python -m build --wheel .
python -m auditwheel repair dist/*.whl