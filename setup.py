#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""
import sys

from setuptools import find_packages, setup


def get_version(filename):
    """Extract the package version."""
    with open(filename, encoding='utf8') as in_fh:
        for line in in_fh:
            if line.startswith('__version__'):
                return line.split('=')[1].strip()[1:-1]
    raise ValueError("Cannot extract version from %s" % filename)


with open('README.rst', encoding='utf8') as readme_file:
    readme = readme_file.read()

try:
    with open('HISTORY.rst', encoding='utf8') as history_file:
        history = history_file.read()
except OSError:
    history = ''

# requirements for use
requirements = [
    'click >= 6.7',
    'jinja2',
    'packaging',
    'pyparsing >= 2.0.2',
    'setuptools',
    'sphinx',
]

# requirements for development (testing, generating docs)
dev_requirements = [
    'black < 23.0',
    'coverage',
    'coveralls',
    'flake8',
    'gitpython',
    'ipython',
    'isort',
    'pdbpp',
    'pre-commit',
    'pylint',
    'pytest',
    'pytest-cov',
    'pytest-xdist',
    'sphinx',
    'sphinx-autobuild',
    'sphinx-autodoc-typehints',
    'sphinx-copybutton',
    'sphinx_rtd_theme',  # for testing only
    'twine',
    'wheel',
]

version = get_version('./src/docs_versions_menu/__init__.py')

setup(
    author="Michael Goerz",
    author_email='mail@michaelgoerz.net',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Environment :: Plugins',
        'Framework :: Sphinx',
        'Framework :: Sphinx :: Extension',
        'Operating System :: OS Independent',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Software Development :: Documentation',
        'Topic :: Utilities',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    description="A versions menu for Sphinx-based documentation",
    python_requires='>=3.7',
    install_requires=requirements,
    extras_require={'dev': dev_requirements},
    license="MIT license",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords=['Doctr', 'Sphinx', 'Github'],
    name='docs_versions_menu',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"": ["_template/*", "_css/*", "_fonts/*"]},
    url='https://github.com/goerz/docs_versions_menu',
    version=version,
    zip_safe=False,
    entry_points='''
        [console_scripts]
        docs-versions-menu=docs_versions_menu.cli:main
    ''',
)
