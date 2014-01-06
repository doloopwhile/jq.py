#!/usr/bin/env python
import io

from setuptools import setup
from distutils.extension import Extension
from Cython.Build import cythonize


with io.open('README.md', encoding='utf-8') as fp:
    long_description = fp.read()


setup(
    install_requires=['cython'],
    ext_modules=cythonize([
        Extension(
            "jq",
            sources=["jq.pyx"],
            libraries=["jq"],
            # extra_link_args=['-static'],
        )
    ]),

    name='jq',
    version='1.0.0',
    description='binding for ./jq JSON processor.',
    long_description=long_description,
    author='OMOTO Kenji',
    url='http://github.com/doloopwhile/jq.py',
    license='MIT License',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: JavaScript',
    ],
)

