import os
import sys
from setuptools import setup, Extension
import pybind11

class get_pybind_include(object):
    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        return pybind11.get_include(self.user)

# Windows (MSVC) ve Linux/Mac (GCC/Clang) için farklı C++17 bayrakları
compile_args = ['/std:c++17', '/O2'] if sys.platform == 'win32' else ['-std=c++17', '-O3']

ext_modules = [
    Extension(
        'url_engine',
        ['src/url_analyzer.cpp'],
        include_dirs=[
            get_pybind_include(),
            get_pybind_include(user=True)
        ],
        language='c++',
        extra_compile_args=compile_args,
    ),
]

setup(
    name='url_engine',
    version='1.0.0',
    description='High-performance C++ URL feature extraction for OmniGuard',
    ext_modules=ext_modules,
    setup_requires=['pybind11>=2.5.0'],
    zip_safe=False,
)