#!/usr/bin/env python
# coding: utf-8
import os
import re
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests>=2.13',
    'tornado>=4.4.2',
    'lxml>=3.7.2',
    'cssselect>=1.0.1',
    'feedparser>=5.2.1',
    'click>=3.3',
    'Babel>=2.3.4',
    'prometheus_client>=0.0.18',
    'raven>=6.3.0',
]

test_requirements = [
    'pytest>=2.6.4',
    'pytest-cov>=1.8.1',
    'responses>=0.3.0'
]

needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []


setup(
    name='critics',
    version=get_version('critics'),
    description="Mobile reviews aggregator",
    long_description=readme + '\n\n' + history,
    author="Ilya Baryshev",
    author_email='baryshev@gmail.com',
    url='https://github.com/coagulant/critics',
    packages=['critics'],
    package_dir={'critics': 'critics'},
    include_package_data=True,
    install_requires=requirements,
    setup_requires=pytest_runner,
    entry_points="""
        [console_scripts]
        critics=critics:main
    """,
    license="BSD",
    zip_safe=False,
    keywords='critics',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
