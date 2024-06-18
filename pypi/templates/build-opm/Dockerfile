FROM quay.io/pypa/manylinux2014_x86_64 as opm_builder
# This is a CentOS 7 based image


# NOTE: We add the OPM repository, see: https://opm-project.org/package/redhat/7/
#   to have the following packages available:
#  - dune-common-devel
#  - dune-geometry-devel
#  - dune-grid-devel
#  - dune-istl-devel
#  - dune-localfunctions-devel
#  - suitesparse-devel
#  - zoltan-devel
# NOTE: We do not unclude libssl-devel (v1.0.2) because we will build a newer version (1.1.1k)
#   of OpenSSL from source. This is needed for Python >= 3.8.0
# NOTE: We do not include python3-devel because we will build Python from source, see comments
#   below.
RUN yum-config-manager --add-repo https://www.opm-project.org/package/opm.repo && \
    yum update -y && yum install -y \
    curl gcc gcc-c++ git \
    vim sudo wget autoconf libtool \
    cmake numpy gcc-gfortran pkgconfig \
    openmpi-devel blas-devel boost-devel \
    ccache tbb-devel SuperLU-devel dune-common-devel dune-geometry-devel \
    dune-grid-devel dune-istl-devel dune-localfunctions-devel \
    suitesparse-devel zoltan-devel \
    bzip2-devel libffi-devel && \
    yum clean all

# Install a recent version of OpenSSL, this is needed for building Python version >= 3.8.0
ARG OPENSSL_VERSION=1.1.1k
RUN cd /tmp && \
    wget https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz && \
    tar xzf openssl-${OPENSSL_VERSION}.tar.gz && \
    cd openssl-${OPENSSL_VERSION} && \
    ./config shared zlib && \
    make && make install

# NOTE: Unfortunately, we cannot use any of the preinstalled Python versions for manylinux2014
#  because they are not built with a shared library or static library.
#  Since we are using embedded Python in OPM, we need to build Python with a shared library.
#
# NOTE: I have tested Python version 3.9 and it worked well with boost 1.74.0, so using
#  3.9.0 as the default version. I also tested Python 3.10.0 and it did not work with
#  boost 1.74.0
ARG PYTHON_VERSION=3.9.0
ARG PYTHON_VERSION_SHORT=3.9

# Download and build Python with shared library
RUN mkdir -p /tmp/python/ && cd /tmp/python && \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations --enable-shared --prefix=/opt/mypython/${PYTHON_VERSION} && \
    make && make install

# Update the shared library cache
RUN echo "/opt/mypython/${PYTHON_VERSION}/lib" >> /etc/ld.so.conf.d/mypython.conf && ldconfig
# Make the new Python the default
ENV PATH=/opt/mypython/${PYTHON_VERSION}/bin:$PATH

# NOTE: "yum install boost boost-devel" will install boost 1.53, which is too old for OPM
#   We could instead install boost 1.69 using "yum install boost169-devel boost169-static"
#   But experiments showed that this version is too low for Python > 3.9.0
#   It also appears that no other version of boost is available in the CentOS 7 repositories,
#   so for more flexibility, we will build boost from source.
#
# NOTE: I found that boost 1.74.0 works well with python 3.9 but not with Python 3.10
#   and higher.
#
# Set the version of Boost to install from source
ARG BOOST_VERSION=1.74.0
ARG BOOST_VERSION_UNDERSCORE=1_74_0
ENV BOOST_INSTALL_DIR=/opt/boost/${BOOST_VERSION}

# The user-config.jam is needed to build boost with the correct python version
COPY user-config.jam /root/

# Download and extract Boost
RUN wget https://boostorg.jfrog.io/artifactory/main/release/${BOOST_VERSION}/source/boost_${BOOST_VERSION_UNDERSCORE}.tar.bz2 && \
    tar --bzip2 -xf boost_${BOOST_VERSION_UNDERSCORE}.tar.bz2 && \
    rm boost_${BOOST_VERSION_UNDERSCORE}.tar.bz2 && \
    cd boost_${BOOST_VERSION_UNDERSCORE} && \
    ./bootstrap.sh --prefix=${BOOST_INSTALL_DIR} && \
    ./b2 install --prefix=${BOOST_INSTALL_DIR} --user-config=/root/user-config.jam -j4 && \
    cd .. && \
    rm -rf boost_${BOOST_VERSION_UNDERSCORE}

# Add Boost library path to ld.so.conf.d and run ldconfig
RUN echo "${BOOST_INSTALL_DIR}/lib" > /etc/ld.so.conf.d/boost.conf && ldconfig

# Apparently, no pybind11-dev package is available with yum, so use pip to install it instead
RUN python3 -m pip install --upgrade pip && \
    pip install pybind11

# Create a new user with the same UID and GID as the host user
ARG HOST_UID
ARG HOST_GID
ARG USERNAME=dockeruser
RUN groupadd -g ${HOST_GID} ${USERNAME} && \
    useradd -u ${HOST_UID} -g ${HOST_GID} -m ${USERNAME}

# Allow the new user to use sudo without a password
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

ENV HOME=/home/${USERNAME}
WORKDIR ${HOME}
COPY --chown=${HOST_UID}:${HOST_GID} ./entrypoint.sh .
RUN chmod +x ${HOME}/entrypoint.sh
# Switch to the new user
ENV PATH=${PATH}:${HOME}/.local/bin
#RUN echo "PATH = $PATH"

USER ${USERNAME}
# NOTE: -DWITH_NATIVE=0 turns off native instruction set tuning, see UseOptimization.cmake
# NOTE: Do not run cmake below with -DBoost_USE_STATIC_LIBS=1 it will undefine
#   the variable BOOST_TEST_ALTERNATIVE_INIT_API which will redefine the signature of
#   the init_unit_test_func function and also lead to a linker error because the of
#   the redefinition of the main() function in the boost library.
#   See:
#   https://github.com/boostorg/test/blob/fd5e60f995604ca64d5194c1e5bd477d194683db/include/boost/test/framework.hpp#L40
# -----------------------------
# Build and install opm-common
# -----------------------------
RUN mkdir -p ${HOME}/opm && cd ${HOME}/opm && \
    git clone https://github.com/OPM/opm-common.git && \
    cd opm-common && mkdir build && cd build && \
    Pybind11_DIR=$(python3 -m pybind11 --cmakedir) && \
    cmake -DPython3_EXECUTABLE=/opt/mypython/${PYTHON_VERSION}/bin/python3 \
     -DPython3_LIBRARY=/opt/mypython/${PYTHON_VERSION}/lib/libpython${PYTHON_VERSION_SHORT}.so \
     -DPython3_INCLUDE_DIR=/opt/mypython/${PYTHON_VERSION}/include/python${PYTHON_VERSION_SHORT} \
     -Dpybind11_DIR=${Pybind11_DIR} \
     -DBOOST_INCLUDEDIR=${BOOST_INSTALL_DIR}/include \
     -DBOOST_LIBRARYDIR=${BOOST_INSTALL_DIR}/lib \
     -DWITH_NATIVE=0 \
     -DBUILD_SHARED_LIBS=OFF -DOPM_ENABLE_PYTHON=ON -DOPM_ENABLE_EMBEDDED_PYTHON=ON .. \
     -DCMAKE_INSTALL_PREFIX=/opt/opm && \
     make -j4 && sudo make install

# NOTE: We can now delete the opm-common directory, since we have installed the libraries
#   and headers in /opt/opm
# -----------------------------
# Build and install opm-grid
# -----------------------------
RUN cd ${HOME}/opm; rm -rf opm-common; git clone https://github.com/OPM/opm-grid.git && \
    cd opm-grid && mkdir build && cd build && \
    cmake -DCMAKE_PREFIX_PATH=/opt/opm \
    -DCMAKE_INSTALL_PREFIX=/opt/opm .. \
    -DBOOST_INCLUDEDIR=${BOOST_INSTALL_DIR}/include \
    -DBOOST_LIBRARYDIR=${BOOST_INSTALL_DIR}/lib \
    -DBUILD_SHARED_LIBS=OFF \
    -DWITH_NATIVE=0 .. && \
     make -j4 && sudo make install

# NOTE: We can now delete the opm-grid directory, since we have installed the libraries
#   and headers in /opt/opm
# -----------------------------
# Build and install opm-models
# -----------------------------
RUN cd ${HOME}/opm; rm -rf opm-grid; git clone https://github.com/OPM/opm-models.git && \
    cd opm-models && mkdir build && cd build && \
    cmake -DCMAKE_PREFIX_PATH=/opt/opm \
    -DCMAKE_INSTALL_PREFIX=/opt/opm .. \
    -DBOOST_INCLUDEDIR=${BOOST_INSTALL_DIR}/include \
    -DBOOST_LIBRARYDIR=${BOOST_INSTALL_DIR}/lib \
    -DBUILD_SHARED_LIBS=OFF \
    -DWITH_NATIVE=0 .. && \
     make -j4 && sudo make install

# NOTE: We can now delete the opm-models directory, since we have installed the libraries
#   and headers in /opt/opm
# -----------------------------
# Build and install opm-simulators
# -----------------------------
    RUN cd ${HOME}/opm; rm -rf opm-models; git clone https://github.com/OPM/opm-simulators.git && \
    cd opm-simulators && mkdir build && cd build && \
    cmake -DCMAKE_PREFIX_PATH=/opt/opm \
    -DCMAKE_INSTALL_PREFIX=/opt/opm .. \
    -DBOOST_INCLUDEDIR=${BOOST_INSTALL_DIR}/include \
    -DBOOST_LIBRARYDIR=${BOOST_INSTALL_DIR}/lib \
    -DBUILD_SHARED_LIBS=OFF \
    -DWITH_NATIVE=0 .. && \
    make -j4 && sudo make install
ENTRYPOINT ["./entrypoint.sh"]
