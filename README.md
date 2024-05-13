# opm-python-test

Testing repository for `opm-python`.

The plan is to create a repository https://github.com/OPM/opm-python/ that will build Python bindings for `opm-common` and `opm-simulators`.
As a first stage in this plan, the current repository `opm-python-test` was created for discussing and preparing the implementation of the `opm-python` repository.

## To build opm-python-test

```
#! /bin/bash

NPROC=5  # Number of build threads when running "make"

build_opm_common() {
   local flags="-DBUILD_SHARED_LIBS=ON"
   git clone git@github.com:OPM/opm-common.git
   cd opm-common
   mkdir build
   cd build
   cmake $flags ..
   make -j$NPROC
   cd ../..
}

build_opm_grid() {
   local flags=""
   git clone git@github.com:OPM/opm-grid.git
   cd opm-grid
   mkdir build
   cd build
   cmake $flags ..
   make -j$NPROC
   cd ../..
}

build_opm_models() {
   local flags=""
   git clone git@github.com:OPM/opm-models.git
   cd opm-models
   mkdir build
   cd build
   cmake $flags ..
   make -j$NPROC
   cd ../..
}

build_opm_simulators() {
   local flags="-DBUILD_SHARED_LIBS=ON"
   git clone git@github.com:OPM/opm-simulators.git
   cd opm-simulators
   mkdir build
   cd build
   cmake $flags ..
   make -j$NPROC
   cd ../..
}

build_opm_python() {
   local flags=""
   git clone git@github.com:hakonhagland/opm-python-test.git
   cd opm-python-test
   mkdir build
   cd build
   cmake $flags ..
   make -j$NPROC
   cd ../..
}

build_opm_common
build_opm_grid
build_opm_models
build_opm_simulators
build_opm_python

```