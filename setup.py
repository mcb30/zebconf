#!/usr/bin/env python3

"""Setup script"""

from setuptools import setup, find_packages

setup(
    name="zebconf",
    description="Zebra printer configuration",
    author="Michael Brown",
    author_email="mbrown@fensystems.co.uk",
    url="https://github.com/unipartdigital/zebconf",
    license="GPLv2+",
    version="0.1.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: "
        "GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python :: 3",
        "Topic :: Printing",
    ],
    packages=find_packages(),
    install_requires=[
        'colorlog',
        'passlib',
        'pyusb',
    ],
    entry_points={
        'console_scripts': [
            'zebconf=zebconf.cli:ZebraCommand.main',
        ],
    },
)
