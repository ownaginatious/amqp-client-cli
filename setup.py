#! /usr/bin/env python
from setuptools import setup, find_packages
from io import open

setup(
    name="amqp_client_cli",
    packages=find_packages(),
    version="0.4",
    description="A command line interface for interacting with amqp exchanges.",
    author="Dillon Dixon",
    url="https://github.com/ownaginatious/amqp-client-cli",
    license="MIT",
    keywords=["amqp", "cli", "client", "rabbitmq", "amq"],
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        line.strip()
        for line in open("requirements.txt", "r", encoding="utf-8").readlines()
    ],
    entry_points={
        "console_scripts": [
            "amqpcli = amqp_client_cli.main:main",
        ],
    },
)
