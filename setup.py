#!/usr/bin/env python

import os
import subprocess
from setuptools import setup
from distutils.extension import Extension
from distutils.command.build_ext import build_ext


def path_in_dir(relative_path):
    return os.path.join(os.path.dirname(__file__), relative_path)


def read_or_empty_string(fname):
    path = path_in_dir(fname)
    if os.path.exists(path):
        return open(path).read()
    else:
        return ""


jq_lib_dir = path_in_dir("_jq")

class jq_build_ext(build_ext):
    def run(self):

        def command(args):
            subprocess.check_call(args, cwd=path_in_dir(jq_lib_dir))

        if os.path.exists(jq_lib_dir):
            command(["git", "checkout", "master"])
            command(["git", "pull"])
        else:
            subprocess.check_call([
                "git", "clone",
                "https://github.com/stedolan/jq.git",
                jq_lib_dir
            ])
            command(["git", "checkout", "master"])

        command(["mkdir", "-p", "m4"])
        command(["autoreconf", "-i"])
        command(["./configure", "CFLAGS=-fPIC"])
        command(["make", "clean"])
        command(["make"])

        build_ext.run(self)


jq_extension = Extension(
    "jq",
    sources=["jq.c"],
    include_dirs=[jq_lib_dir],
    #libraries=["jq"],
    extra_objects=[os.path.join(jq_lib_dir, ".libs/libjq.a")],
    #library_dirs=[os.path.join(jq_lib_dir, ".libs")],
)

setup(
    name='jq',
    version='0.1.0',
    description='jq is a lightweight and flexible JSON processor.',
    long_description=read_or_empty_string("README"),
    author='Michael Williamson',
    url='http://github.com/mwilliamson/jq.py',
    license='BSD 2-Clause',
    ext_modules = [jq_extension],
    cmdclass={"build_ext": jq_build_ext},
)

