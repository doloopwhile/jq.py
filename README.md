# pyjq: Binding for jq JSON Processor

pyjq is a Python bindings for *[jq](http://stedolan.github.io/jq/)*.

You can seamlessly call *jq* script (like regular expression)
and process plain python data structure.

## Examples

    >>> data = dict(
    ...     parameters= [
    ...         dict(name="PKG_TAG_NAME", value="trunk"),
    ...         dict(name="GIT_COMMIT", value="master"),
    ...         dict(name="TRIGGERED_JOB", value="trunk-buildall")
    ...     ],
    ...     id="2013-12-27_00-09-37",
    ...     changeSet=dict(items=[], kind="git"),
    ... )
    >>> import jq
    >>> jq.first('.parameters[] | {"param_name": .name, "param_type":.type}', data)
    {'param_type': None, 'param_name': 'PKG_TAG_NAME'}

## Limitation
jq is a JSON Processor.
Therefore pyjq is able to process only "JSON compatible" data
(object made only from str, int, float, list, dict).


## Install
As usual:

    pip install pyjq

For your information, https://pypi.python.org/pypi/jq is a also jq bindings
but different and incompatible with pyjq.


## Build from source code
### Build jq
You have to build and install *jq* library before you build this module.

1. ./jq requires following packages

  - Flex
  - Bison
  - GCC
  - Make
  - Autotools

These will be installed by your system's package manager (apt, yum, or else).

2. Checkout source code from github

    git clone https://github.com/stedolan/jq
    cd jq
    git checkout jq-1.3

Where, you can checkout `master` branch or newer release than jq-1.3.
However, author of pyjq have not build with any release other than jq-1.3.

3. Build and install *jq*

    autoreconf -i
    ./configure
    make
    sudo make install

4. Update cache for library
Some system have cached list of dynamic link libraries.
In such system, library of jq is not loaded and importing python binding fails.

Command to refresh the cache is system specific.
In the case Linux Mint 14:

    ldconfig

### Install pyjq
*setuptools* and *cython* are required to build and to install this module.

You can build and install this module by usual way.

    python setup.py install


## Q&A
### How can I process json string got from API by pyjq?
You should apply `json.loads` in the standard library before pass to pyjq.

## License
Copyright (c) 2014 OMOTO Kenji. Released under the MIT license. See LICENSE for details.
