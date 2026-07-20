cmake_minimum_required(VERSION 3.15)
project(BOMGeneratorCore LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(PYBIND11_FINDPYTHON ON)

include(FetchContent)
FetchContent_Declare(
pybind11
GIT_REPOSITORY https://github.com/pybind/pybind11.git
GIT_TAG        v2.13.0 # Upgraded to newer version to fix CMake 4.4 warnings
)
FetchContent_MakeAvailable(pybind11)

pybind11_add_module(bom_core python_bridge.cpp)
target_compile_options(bom_core PRIVATE -O3)