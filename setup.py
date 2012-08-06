import os
from distutils.core import setup

try:
    import setuptools
except ImportError:
    pass


with open(os.path.abspath('README.md')) as f:
    long_description = f.read()

setup(

    name="pycacher",
    version="0.0.1",
    packages=['pycacher'],
    author="Garindra Prahandono",
    author_email="garindraprahandono@gmail.com",
    url='http://pycacher.readthedocs.org',
    description="pycacher is a python module which enables easy caching layer via function decorators, batcher, etc.",
    long_description=long_description
)
