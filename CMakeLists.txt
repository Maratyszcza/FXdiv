CMAKE_MINIMUM_REQUIRED(VERSION 2.8.12 FATAL_ERROR)

INCLUDE(GNUInstallDirs)

# ---[ Project
PROJECT(FXdiv LANGUAGES CXX)

# ---[ Options.
OPTION(FXDIV_BUILD_TESTS "Build FXdiv unit tests" ON)
OPTION(FXDIV_BUILD_BENCHMARKS "Build FXdiv micro-benchmarks" ON)

# ---[ CMake options
IF(FXDIV_BUILD_TESTS)
  ENABLE_TESTING()
ENDIF()

# ---[ Build flags
IF(NOT MSVC)
  SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
ENDIF()

# ---[ Download deps
SET(CONFU_DEPENDENCIES_SOURCE_DIR ${CMAKE_SOURCE_DIR}/deps
  CACHE PATH "Confu-style dependencies source directory")
SET(CONFU_DEPENDENCIES_BINARY_DIR ${CMAKE_BINARY_DIR}/deps
  CACHE PATH "Confu-style dependencies binary directory")

IF(NOT TARGET gtest)
  CONFIGURE_FILE(cmake/DownloadGoogleTest.cmake "${CMAKE_BINARY_DIR}/googletest-download/CMakeLists.txt")
  EXECUTE_PROCESS(COMMAND "${CMAKE_COMMAND}" -G "${CMAKE_GENERATOR}" .
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/googletest-download")
  EXECUTE_PROCESS(COMMAND "${CMAKE_COMMAND}" --build .
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/googletest-download")
ENDIF()

IF(NOT TARGET benchmark)
  CONFIGURE_FILE(cmake/DownloadGoogleBenchmark.cmake "${CMAKE_BINARY_DIR}/googlebenchmark-download/CMakeLists.txt")
  EXECUTE_PROCESS(COMMAND "${CMAKE_COMMAND}" -G "${CMAKE_GENERATOR}" .
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/googlebenchmark-download")
  EXECUTE_PROCESS(COMMAND "${CMAKE_COMMAND}" --build .
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/googlebenchmark-download")
ENDIF()

# ---[ FXdiv library
ADD_LIBRARY(fxdiv INTERFACE)
TARGET_INCLUDE_DIRECTORIES(fxdiv INTERFACE include)

INSTALL(FILES include/fxdiv.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

IF(FXDIV_BUILD_TESTS)
  # ---[ Build google test
  IF(NOT TARGET gtest)
    SET(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    ADD_SUBDIRECTORY(
      "${CONFU_DEPENDENCIES_SOURCE_DIR}/googletest"
      "${CONFU_DEPENDENCIES_BINARY_DIR}/googletest")
  ENDIF()

  ADD_EXECUTABLE(multiply-high-test test/multiply-high.cc)
  TARGET_LINK_LIBRARIES(multiply-high-test fxdiv gtest gtest_main)
  ADD_TEST(multiply-high multiply-high-test)

  ADD_EXECUTABLE(quotient-test test/quotient.cc)
  TARGET_LINK_LIBRARIES(quotient-test fxdiv gtest gtest_main)
  ADD_TEST(quotient quotient-test)
ENDIF()

IF(FXDIV_BUILD_BENCHMARKS)
  # ---[ Build google benchmark
  IF(NOT TARGET benchmark)
    SET(BENCHMARK_ENABLE_TESTING ON CACHE BOOL "" FORCE)
    ADD_SUBDIRECTORY(
      "${CONFU_DEPENDENCIES_SOURCE_DIR}/googlebenchmark"
      "${CONFU_DEPENDENCIES_BINARY_DIR}/googlebenchmark")
  ENDIF()

  ADD_EXECUTABLE(init-bench bench/init.cc)
  TARGET_LINK_LIBRARIES(init-bench fxdiv benchmark)

  ADD_EXECUTABLE(multiply-bench bench/multiply.cc)
  TARGET_LINK_LIBRARIES(multiply-bench fxdiv benchmark)

  ADD_EXECUTABLE(divide-bench bench/divide.cc)
  TARGET_LINK_LIBRARIES(divide-bench fxdiv benchmark)

  ADD_EXECUTABLE(quotient-bench bench/quotient.cc)
  TARGET_LINK_LIBRARIES(quotient-bench fxdiv benchmark)

  ADD_EXECUTABLE(round-down-bench bench/round-down.cc)
  TARGET_LINK_LIBRARIES(round-down-bench fxdiv benchmark)
ENDIF()
