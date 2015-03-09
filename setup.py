#!/usr/bin/env python
# coding: utf-8
import os
import re
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


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
    'requests',
    'tornado',
    'lxml',
    'cssselect',
    'feedparser',
    'click',
    'pytils'
]

test_requirements = [
    'pytest',
    'pytest-cov',
    'responses'
]

setup(
    name='critics',
    version='0.1.0',
    description="Mobile reviews aggregator",
    long_description=readme + '\n\n' + history,
    author="Ilya Baryshev",
    author_email='baryshev@gmail.com',
    url='https://github.com/coagulant/critics',
    packages=['critics'],
    package_dir={'critics': 'critics'},
    include_package_data=True,
    install_requires=requirements,
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass={'test': PyTest},
)
