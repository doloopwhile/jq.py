#!/usr/bin/env python
import os
import subprocess
from setuptools import setup
from distutils.extension import Extension
from Cython.Build import cythonize



setup(
    name='jq',
    ext_modules = cythonize([
        Extension(
            "jq",
            sources=["jq.pyx"],
            include_dirs=['_jq'],
            extra_objects=["_jq/.libs/libjq.a"],
            extra_compile_args=['-std=c99'],
        )
    ],
    )
)

