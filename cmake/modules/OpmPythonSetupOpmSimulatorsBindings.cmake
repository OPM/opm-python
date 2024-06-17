# opm-simulators python bindings
function (build_opm_simulators_pybind11_module)
  foreach (_file IN LISTS PYTHON_SIMULATORS_CXX_SOURCE_FILES)
    list (APPEND SIMULATORS_CXX_SOURCE_FILES
          "${PROJECT_SOURCE_DIR}/pybind11/opmsimulators/${_file}")
  endforeach (_file)

  set (MODULE_VERSION_OBJECT_FILE "${opm-simulators_DIR}/CMakeFiles/moduleVersion.dir/opm/simulators/utils/moduleVersion.cpp.o")

  pybind11_add_module(simulators
    ${SIMULATORS_CXX_SOURCE_FILES}
    "${DOCSTRINGS_GENERATED_HEADER_PATH}"  # Include the generated .hpp as a source file
    "${MODULE_VERSION_OBJECT_FILE}"
  )
  # Make sure the module depends on the generated header file
  add_dependencies(simulators pyblackoil_generate_docstring_hpp)
  add_dependencies(simulators common_generate_docstring_hpp)

  set_target_properties(
           simulators PROPERTIES
           LIBRARY_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/${GENERATED_PROJECT_DIR}/src/opm/simulators")

  target_link_libraries(simulators PRIVATE opmsimulators )

  # Add the build directory where the generated hpp file will be
  # to the include directories for the target
  target_include_directories(simulators PRIVATE "${PROJECT_BINARY_DIR}/${TEMP_GEN_DIR}")
endfunction()

build_opm_simulators_pybind11_module()
