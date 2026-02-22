cmake_minimum_required(VERSION 3.12)
project(url_engine)

# Find pybind11
find_package(pybind11 REQUIRED)

# Create the module
pybind11_add_module(url_engine src/url_analyzer.cpp)

# Optimize for performance
target_compile_options(url_engine PRIVATE -O3 -Wall -Wextra)