import os
from distutils.core import setup

from pycacher import __version__

try:
    import setuptools
except ImportError:
    pass


with open(os.path.abspath('README.md')) as f:
    long_description = f.read()

setup(

    name="pycacher",
    version=__version__,
    packages=['pycacher'],
    author="Garindra Prahandono",
    install_requires=['python-memcached'],
    author_email="garindraprahandono@gmail.com",
    url='http://pycacher.readthedocs.org',
    download_url=('http://cloud.github.com/downloads/garindra/'
                      'pycacher/pycacher-%s.tar.gz' % __version__),
    description="pycacher is a python module which enables easy caching layer via function decorators, batcher, etc.",
    test_suite='nose.collector',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python']
)
