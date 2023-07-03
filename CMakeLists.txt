CMAKE_MINIMUM_REQUIRED(VERSION 3.5 FATAL_ERROR)

# ---[ Project
PROJECT(FXdiv C CXX)

# ---[ Options.
OPTION(FXDIV_USE_INLINE_ASSEMBLY "Allow use of inline assembly in FXdiv" OFF)
IF("${CMAKE_SOURCE_DIR}" STREQUAL "${PROJECT_SOURCE_DIR}")
  OPTION(FXDIV_BUILD_TESTS "Build FXdiv unit tests" ON)
  OPTION(FXDIV_BUILD_BENCHMARKS "Build FXdiv micro-benchmarks" ON)
ELSE()
  SET(FXDIV_BUILD_TESTS OFF CACHE BOOL "Build FXdiv unit tests")
  SET(FXDIV_BUILD_BENCHMARKS OFF CACHE BOOL "Build FXdiv micro-benchmarks")
ENDIF()
OPTION(USE_SYSTEM_LIBS "Use system libraries instead of downloading and building them" OFF)
OPTION(USE_SYSTEM_GOOGLEBENCHMARK "Use system Google Benchmark library instead of downloading and building it" ${USE_SYSTEM_LIBS})
OPTION(USE_SYSTEM_GOOGLETEST "Use system Google Test library instead of downloading and building it" ${USE_SYSTEM_LIBS})

# ---[ CMake options
INCLUDE(GNUInstallDirs)

IF(FXDIV_BUILD_TESTS)
  ENABLE_TESTING()
ENDIF()

# ---[ Download deps
IF(FXDIV_BUILD_TESTS)
  IF(USE_SYSTEM_GOOGLETEST)
    FIND_PACKAGE(GTest REQUIRED)
  ELSEIF(NOT DEFINED GOOGLETEST_SOURCE_DIR)
    MESSAGE(STATUS "Downloading Google Test to ${CMAKE_BINARY_DIR}/googletest-source (define GOOGLETEST_SOURCE_DIR to avoid it)")
    CONFIGURE_FILE(cmake/DownloadGoogleTest.cmake "${CMAKE_BINARY_DIR}/googletest-download/CMakeLists.txt")
    EXECUTE_PROCESS(COMMAND "${CMAKE_COMMAND}" -G "${CMAKE_GENERATOR}" .
      WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/googletest-download")
    EXECUTE_PROCESS(COMMAND "${CMAKE_COMMAND}" --build .
      WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/googletest-download")
    SET(GOOGLETEST_SOURCE_DIR "${CMAKE_BINARY_DIR}/googletest-source" CACHE STRING "Google Test source directory")
  ENDIF()
ENDIF()

IF(FXDIV_BUILD_BENCHMARKS)
  IF(USE_SYSTEM_GOOGLEBENCHMARK)
    FIND_PACKAGE(benchmark REQUIRED)
  ELSEIF(NOT DEFINED GOOGLEBENCHMARK_SOURCE_DIR)
    MESSAGE(STATUS "Downloading Google Benchmark to ${CMAKE_BINARY_DIR}/googlebenchmark-source (define GOOGLEBENCHMARK_SOURCE_DIR to avoid it)")
    CONFIGURE_FILE(cmake/DownloadGoogleBenchmark.cmake "${CMAKE_BINARY_DIR}/googlebenchmark-download/CMakeLists.txt")
    EXECUTE_PROCESS(COMMAND "${CMAKE_COMMAND}" -G "${CMAKE_GENERATOR}" .
      WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/googlebenchmark-download")
    EXECUTE_PROCESS(COMMAND "${CMAKE_COMMAND}" --build .
      WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/googlebenchmark-download")
    SET(GOOGLEBENCHMARK_SOURCE_DIR "${CMAKE_BINARY_DIR}/googlebenchmark-source" CACHE STRING "Google Benchmark source directory")
  ENDIF()
ENDIF()

# ---[ FXdiv library
ADD_LIBRARY(fxdiv INTERFACE)
TARGET_INCLUDE_DIRECTORIES(fxdiv INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
IF(FXDIV_USE_INLINE_ASSEMBLY)
  TARGET_COMPILE_DEFINITIONS(fxdiv INTERFACE FXDIV_USE_INLINE_ASSEMBLY=1)
ELSE()
  TARGET_COMPILE_DEFINITIONS(fxdiv INTERFACE FXDIV_USE_INLINE_ASSEMBLY=0)
ENDIF()

INCLUDE(CMakePackageConfigHelpers)
CONFIGURE_PACKAGE_CONFIG_FILE(
  ${CMAKE_CURRENT_SOURCE_DIR}/cmake/${CMAKE_PROJECT_NAME}Config.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}Config.cmake
  INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${CMAKE_PROJECT_NAME}
)

INSTALL(TARGETS fxdiv EXPORT ${CMAKE_PROJECT_NAME}Targets)
INSTALL(EXPORT ${CMAKE_PROJECT_NAME}Targets
  FILE ${CMAKE_PROJECT_NAME}Config.cmake
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${CMAKE_PROJECT_NAME}
)
INSTALL(DIRECTORY include/ DESTINATION include)

IF(FXDIV_BUILD_TESTS)
  # ---[ Build google test
  IF(NOT TARGET gtest AND NOT USE_SYSTEM_GOOGLETEST)
    SET(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    ADD_SUBDIRECTORY(
      "${GOOGLETEST_SOURCE_DIR}"
      "${CMAKE_BINARY_DIR}/googletest")
  ENDIF()

  ADD_EXECUTABLE(multiply-high-test test/multiply-high.cc)
  SET_TARGET_PROPERTIES(multiply-high-test PROPERTIES
    CXX_STANDARD 11
    CXX_EXTENSIONS YES)
  TARGET_LINK_LIBRARIES(multiply-high-test fxdiv gtest gtest_main)
  ADD_TEST(multiply-high multiply-high-test)

  ADD_EXECUTABLE(quotient-test test/quotient.cc)
  SET_TARGET_PROPERTIES(quotient-test PROPERTIES
    CXX_STANDARD 11
    CXX_EXTENSIONS YES)
  TARGET_LINK_LIBRARIES(quotient-test fxdiv gtest gtest_main)
  ADD_TEST(quotient quotient-test)
ENDIF()

IF(FXDIV_BUILD_BENCHMARKS)
  # ---[ Build google benchmark
  IF(NOT TARGET benchmark AND NOT USE_SYSTEM_GOOGLEBENCHMARK)
    SET(BENCHMARK_ENABLE_TESTING OFF CACHE BOOL "" FORCE)
    ADD_SUBDIRECTORY(
      "${GOOGLEBENCHMARK_SOURCE_DIR}"
      "${CMAKE_BINARY_DIR}/googlebenchmark")
  ENDIF()

  ADD_EXECUTABLE(init-bench bench/init.cc)
  SET_TARGET_PROPERTIES(init-bench PROPERTIES
    CXX_STANDARD 11
    CXX_EXTENSIONS YES)
  TARGET_LINK_LIBRARIES(init-bench fxdiv benchmark)

  ADD_EXECUTABLE(multiply-bench bench/multiply.cc)
  SET_TARGET_PROPERTIES(multiply-bench PROPERTIES
    CXX_STANDARD 11
    CXX_EXTENSIONS YES)
  TARGET_LINK_LIBRARIES(multiply-bench fxdiv benchmark)

  ADD_EXECUTABLE(divide-bench bench/divide.cc)
  SET_TARGET_PROPERTIES(divide-bench PROPERTIES
    CXX_STANDARD 11
    CXX_EXTENSIONS YES)
  TARGET_LINK_LIBRARIES(divide-bench fxdiv benchmark)

  ADD_EXECUTABLE(quotient-bench bench/quotient.cc)
  SET_TARGET_PROPERTIES(quotient-bench PROPERTIES
    CXX_STANDARD 11
    CXX_EXTENSIONS YES)
  TARGET_LINK_LIBRARIES(quotient-bench fxdiv benchmark)

  ADD_EXECUTABLE(round-down-bench bench/round-down.cc)
  SET_TARGET_PROPERTIES(round-down-bench PROPERTIES
    CXX_STANDARD 11
    CXX_EXTENSIONS YES)
  TARGET_LINK_LIBRARIES(round-down-bench fxdiv benchmark)
ENDIF()
